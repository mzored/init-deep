"""CLI entry point for init-deep."""

import argparse
import sys
from pathlib import Path

from .config import load_config
from .selection import resolve_targets
from .targets.registry import create_default_registry


def _project_root() -> Path:
    """Walk up from this file to find the repo root (contains source/)."""
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "source").is_dir():
            return parent
    raise RuntimeError("Cannot locate project root")


def _ensure_tools_importable(root: Path) -> None:
    """Add the project root to sys.path so ``tools.init_deep`` is importable."""
    tools_parent = str(root)
    if tools_parent not in sys.path:
        sys.path.insert(0, tools_parent)


def _resolve_selected_targets(args: argparse.Namespace) -> list[str]:
    """Load config and resolve target selection from CLI flags."""
    root = _project_root()
    config_path = Path(args.config) if args.config else root / ".init-deep.toml"
    config = load_config(config_path)

    registry = create_default_registry()
    available = registry.list_targets()

    only = [t.strip() for t in args.only.split(",")] if args.only else None
    skip = [name for name in available if getattr(args, f"skip_{name}", False)]

    return resolve_targets(available, config.targets, only=only, skip=skip or None)


def _cmd_build(args: argparse.Namespace) -> int:
    root = _project_root()
    _ensure_tools_importable(root)

    selected = _resolve_selected_targets(args)
    print(f"Targets: {', '.join(selected)}")

    # Import lazily so the module-level sys.path tweak takes effect first.
    from tools.init_deep.source import load_canonical_source
    from tools.init_deep.renderers import render_distribution
    from tools.init_deep.paths import managed_paths

    from .planner import (
        plan_build,
        format_plan_table,
        format_plan_json,
        format_plan_diff,
    )

    source = load_canonical_source(root / "source/init-deep/canonical.md")
    outputs = render_distribution(source)
    managed = managed_paths(root)

    # --dry-run, --diff, --json: compute plan without writing
    dry_run = getattr(args, "dry_run", False)
    show_diff = getattr(args, "diff", False)
    show_json = getattr(args, "json", False)

    if dry_run or show_diff or show_json:
        plan = plan_build(outputs, root, managed, prune=True)
        if show_json:
            print(format_plan_json(plan))
        elif show_diff:
            print(format_plan_diff(plan, outputs, root))
        else:
            print(format_plan_table(plan))
        return 0

    # Normal build
    expected_paths = {root / relative_path for relative_path in outputs}

    for stale_path in managed - expected_paths:
        stale_path.unlink()

    for relative_path, content in outputs.items():
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    root = _project_root()
    _ensure_tools_importable(root)

    selected = _resolve_selected_targets(args)
    print(f"Targets: {', '.join(selected)}")

    from difflib import unified_diff
    from tools.init_deep.source import load_canonical_source
    from tools.init_deep.renderers import render_distribution
    from tools.init_deep.paths import managed_paths

    from .planner import plan_build, format_plan_diff

    source = load_canonical_source(root / "source/init-deep/canonical.md")
    outputs = render_distribution(source)
    managed = managed_paths(root)

    show_diff = getattr(args, "diff", False)

    if show_diff:
        plan = plan_build(outputs, root, managed)
        print(format_plan_diff(plan, outputs, root))
        has_issues = bool(plan.writes or plan.deletes)
        return 1 if has_issues else 0

    expected_paths = {root / rp for rp in outputs}
    errors = 0

    for stale in sorted(managed - expected_paths):
        print(f"STALE  {stale.relative_to(root)}")
        errors += 1

    for relative_path, expected in sorted(outputs.items()):
        dest = root / relative_path
        if not dest.exists():
            print(f"MISSING {relative_path}")
            errors += 1
            continue
        actual = dest.read_text(encoding="utf-8")
        if actual != expected:
            diff = unified_diff(
                actual.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=f"a/{relative_path}",
                tofile=f"b/{relative_path}",
            )
            sys.stdout.writelines(diff)
            errors += 1

    if errors:
        print(f"\n{errors} file(s) out of sync — run: python3 scripts/build_init_deep.py")
        return 1
    print("All generated files are in sync.")
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    from .linter import lint_command

    root = _project_root()
    spec_dir = root / "source" / "commands" / args.command_name
    if not spec_dir.is_dir():
        print(f"error: command directory not found: {spec_dir}", file=sys.stderr)
        return 1

    diagnostics = lint_command(spec_dir)
    if not diagnostics:
        print("lint: clean")
        return 0

    has_errors = False
    for d in diagnostics:
        print(d)
        if d.severity == "error":
            has_errors = True

    errors = sum(1 for d in diagnostics if d.severity == "error")
    warnings = sum(1 for d in diagnostics if d.severity == "warning")
    print(f"\n{errors} error(s), {warnings} warning(s)")
    return 1 if has_errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="init-deep",
        description="Multi-platform AI documentation compiler",
    )
    sub = parser.add_subparsers(dest="command")

    # Shared target-selection flags for build and check
    registry = create_default_registry()
    target_names = registry.list_targets()

    for name, help_text in [
        ("build", "Regenerate all platform adapters"),
        ("check", "Validate generated artifacts match canonical source"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument(
            "--config",
            default=None,
            help="Path to .init-deep.toml config file",
        )
        sp.add_argument(
            "--only",
            default=None,
            help="Comma-separated list of targets to generate (e.g. claude,copilot)",
        )
        for tname in target_names:
            sp.add_argument(
                f"--skip-{tname}",
                dest=f"skip_{tname}",
                action="store_true",
                default=False,
                help=f"Skip the {tname} target",
            )

        # --diff is available on both build and check
        sp.add_argument(
            "--diff",
            action="store_true",
            default=False,
            help="Show unified diffs of changes without writing files",
        )

        # --dry-run and --json are build-only
        if name == "build":
            sp.add_argument(
                "--dry-run",
                action="store_true",
                default=False,
                help="Show what would happen without writing files",
            )
            sp.add_argument(
                "--json",
                action="store_true",
                default=False,
                help="Output build plan as machine-readable JSON",
            )

    # lint subcommand
    lint_parser = sub.add_parser(
        "lint", help="Validate source schema and semantics"
    )
    lint_parser.add_argument(
        "--command",
        dest="command_name",
        default="init-deep",
        help="Command to lint (default: init-deep)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    dispatch = {
        "build": _cmd_build,
        "check": _cmd_check,
        "lint": _cmd_lint,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
