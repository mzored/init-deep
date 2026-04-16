"""Workspace health validator."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from .config import load_config
from .targets.registry import create_default_registry


@dataclass(frozen=True)
class HealthCheck:
    """Result of a single health check."""

    name: str
    status: str  # "ok", "warning", "error"
    message: str


def run_doctor(root: Path) -> list[HealthCheck]:
    """Run all health checks against the workspace at *root*."""
    checks: list[HealthCheck] = []

    checks.append(_check_python_version())
    checks.append(_check_source_exists(root))
    checks.extend(_check_config(root))
    checks.extend(_check_artifacts(root))
    checks.extend(_check_stale_legacy(root))
    checks.extend(_check_drift(root))

    return checks


# -- individual checks -------------------------------------------------------


def _check_python_version() -> HealthCheck:
    v = sys.version_info
    if v >= (3, 11):
        return HealthCheck("python-version", "ok", f"Python {v.major}.{v.minor}")
    return HealthCheck(
        "python-version",
        "error",
        f"Python {v.major}.{v.minor} (requires 3.11+)",
    )


def _check_source_exists(root: Path) -> HealthCheck:
    new_format = root / "source" / "commands" / "init-deep" / "spec.toml"
    legacy = root / "source" / "init-deep" / "canonical.md"
    if new_format.exists():
        return HealthCheck("source", "ok", "New format (spec.toml + body.md)")
    if legacy.exists():
        return HealthCheck("source", "ok", "Legacy format (canonical.md)")
    return HealthCheck("source", "error", "No source found")


def _check_config(root: Path) -> list[HealthCheck]:
    checks: list[HealthCheck] = []
    config_path = root / ".init-deep.toml"

    if not config_path.exists():
        checks.append(
            HealthCheck("config", "ok", "No .init-deep.toml (using defaults)")
        )
        return checks

    try:
        config = load_config(config_path)
        checks.append(
            HealthCheck(
                "config",
                "ok",
                f"Loaded .init-deep.toml (profile={config.profile})",
            )
        )

        # Validate that configured targets actually exist in the registry.
        registry = create_default_registry()
        available = set(registry.list_targets())
        for t in config.targets:
            if t not in available:
                checks.append(
                    HealthCheck(
                        "config-target",
                        "warning",
                        f"Unknown target '{t}' in config",
                    )
                )
    except Exception as exc:
        checks.append(
            HealthCheck("config", "error", f"Failed to parse .init-deep.toml: {exc}")
        )

    return checks


def _check_artifacts(root: Path) -> list[HealthCheck]:
    checks: list[HealthCheck] = []

    from .build import build_v2

    source_dir = root / "source" / "commands" / "init-deep"
    if not source_dir.is_dir():
        # Fall back to legacy location — but build_v2 expects a directory,
        # so just report that we can't check artifacts.
        return [
            HealthCheck(
                "artifacts",
                "warning",
                "Cannot check artifacts (new-format source directory not found)",
            )
        ]

    try:
        outputs = build_v2(source_dir)
    except Exception:
        return [
            HealthCheck(
                "artifacts",
                "warning",
                "Could not render artifacts for checking",
            )
        ]

    missing = [rp for rp in sorted(outputs) if not (root / rp).exists()]

    if missing:
        checks.append(
            HealthCheck(
                "artifacts",
                "warning",
                f"Missing artifacts: {', '.join(missing)}",
            )
        )
    else:
        checks.append(
            HealthCheck("artifacts", "ok", f"All {len(outputs)} artifacts present")
        )

    # Size-budget checks
    registry = create_default_registry()
    for target_name in registry.list_targets():
        plugin = registry.get(target_name)
        if plugin is None:
            continue
        caps = plugin.capabilities()
        if caps.size_budget_bytes is None:
            continue
        for relpath, content in outputs.items():
            if target_name in relpath.lower():
                size = len(content.encode("utf-8"))
                if size > caps.size_budget_bytes:
                    checks.append(
                        HealthCheck(
                            "size-budget",
                            "warning",
                            f"{relpath} ({size:,} bytes) exceeds "
                            f"{target_name} budget ({caps.size_budget_bytes:,} bytes)",
                        )
                    )

    return checks


def _check_stale_legacy(root: Path) -> list[HealthCheck]:
    checks: list[HealthCheck] = []
    stale_names = [".windsurfrules", ".clinerules"]
    for filename in stale_names:
        if (root / filename).exists():
            checks.append(
                HealthCheck(
                    "stale-legacy",
                    "warning",
                    f"Legacy file '{filename}' exists "
                    "-- consider removing if using modern mode",
                )
            )
    return checks


def _check_drift(root: Path) -> list[HealthCheck]:
    registry_path = root / "targets" / "registry.toml"
    if not registry_path.exists():
        return []

    from .drift import check_drift, load_registry_meta

    try:
        metas = load_registry_meta(registry_path)
    except Exception as exc:
        return [
            HealthCheck("drift", "warning", f"Failed to load registry.toml: {exc}")
        ]

    warnings = check_drift(metas)
    if warnings:
        checks: list[HealthCheck] = []
        for w in warnings:
            checks.append(HealthCheck("drift", "warning", w.message))
        return checks
    return [
        HealthCheck("drift", "ok", f"All {len(metas)} targets reviewed recently")
    ]


# -- formatting ---------------------------------------------------------------


def format_doctor_output(checks: list[HealthCheck]) -> str:
    """Format health checks for terminal output."""
    icons = {"ok": "+", "warning": "!", "error": "x"}
    lines = [
        f"  [{icons.get(c.status, '?')}] {c.name}: {c.message}" for c in checks
    ]

    errors = sum(1 for c in checks if c.status == "error")
    warnings = sum(1 for c in checks if c.status == "warning")
    lines.append(f"\n{errors} error(s), {warnings} warning(s)")
    return "\n".join(lines)
