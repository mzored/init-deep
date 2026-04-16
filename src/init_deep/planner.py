"""Build planner — computes actions without side effects."""

from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path


@dataclass(frozen=True)
class BuildAction:
    """A single planned build action."""

    op: str  # "write", "skip", "delete"
    target: str  # target name (e.g. "claude")
    relpath: str  # relative output path
    status: str  # "changed", "unchanged", "new", "stale"
    reason: str  # human-readable reason


@dataclass
class BuildPlan:
    """Complete build plan."""

    actions: list[BuildAction]

    @property
    def writes(self) -> list[BuildAction]:
        return [a for a in self.actions if a.op == "write"]

    @property
    def skips(self) -> list[BuildAction]:
        return [a for a in self.actions if a.op == "skip"]

    @property
    def deletes(self) -> list[BuildAction]:
        return [a for a in self.actions if a.op == "delete"]


def plan_build(
    outputs: dict[str, str],
    root: Path,
    managed: set[Path],
    prune: bool = False,
) -> BuildPlan:
    """Plan a build by comparing expected outputs to current files on disk.

    Args:
        outputs: dict of relpath -> content (what renderers produce)
        root: project root
        managed: set of currently managed paths on disk
        prune: whether to delete stale files
    """
    actions: list[BuildAction] = []
    expected_paths: set[Path] = set()

    for relpath, content in sorted(outputs.items()):
        path = root / relpath
        expected_paths.add(path)

        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current == content:
                actions.append(BuildAction(
                    op="skip",
                    target=_infer_target(relpath),
                    relpath=relpath,
                    status="unchanged",
                    reason="content matches",
                ))
            else:
                actions.append(BuildAction(
                    op="write",
                    target=_infer_target(relpath),
                    relpath=relpath,
                    status="changed",
                    reason="content differs",
                ))
        else:
            actions.append(BuildAction(
                op="write",
                target=_infer_target(relpath),
                relpath=relpath,
                status="new",
                reason="file does not exist",
            ))

    # Stale files
    for stale_path in sorted(managed - expected_paths):
        relpath = str(stale_path.relative_to(root))
        actions.append(BuildAction(
            op="delete" if prune else "skip",
            target=_infer_target(relpath),
            relpath=relpath,
            status="stale",
            reason="not in expected outputs" + (" + pruned" if prune else ""),
        ))

    return BuildPlan(actions=actions)


def _infer_target(relpath: str) -> str:
    """Infer target name from a relative path."""
    if "cursor" in relpath:
        return "cursor"
    if "copilot" in relpath:
        return "copilot"
    if "gemini" in relpath:
        return "gemini"
    if "windsurf" in relpath:
        return "windsurf"
    if "cline" in relpath:
        return "cline"
    if "skill" in relpath:
        return "claude"
    return "unknown"


def format_plan_table(plan: BuildPlan) -> str:
    """Format plan as a human-readable table."""
    if not plan.actions:
        return "No actions needed."

    lines: list[str] = []
    lines.append(
        f"{'Op':<8} {'Target':<10} {'Artifact':<50} {'Status':<12} {'Reason'}"
    )
    lines.append("-" * 95)
    for a in plan.actions:
        lines.append(
            f"{a.op:<8} {a.target:<10} {a.relpath:<50} {a.status:<12} {a.reason}"
        )
    return "\n".join(lines)


def format_plan_json(plan: BuildPlan) -> str:
    """Format plan as JSON."""
    return json.dumps(
        [
            {
                "op": a.op,
                "target": a.target,
                "relpath": a.relpath,
                "status": a.status,
                "reason": a.reason,
            }
            for a in plan.actions
        ],
        indent=2,
    )


def format_plan_diff(
    plan: BuildPlan, outputs: dict[str, str], root: Path
) -> str:
    """Format plan as unified diff for changed files."""
    diffs: list[str] = []
    for action in plan.actions:
        if action.status in ("changed", "new"):
            path = root / action.relpath
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            expected = outputs.get(action.relpath, "")
            diff = "".join(unified_diff(
                current.splitlines(keepends=True),
                expected.splitlines(keepends=True),
                fromfile=action.relpath,
                tofile=f"{action.relpath} (generated)",
            ))
            if diff:
                diffs.append(diff)
    return "\n".join(diffs) if diffs else "No differences."
