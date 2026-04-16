"""Upstream target-drift monitoring."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class TargetMeta:
    """Metadata about a target platform from registry.toml."""

    name: str
    doc_url: str
    last_reviewed: date
    status: str  # "stable", "beta", "legacy"
    notes: str = ""


@dataclass(frozen=True)
class DriftWarning:
    """Warning for a target that hasn't been reviewed recently."""

    target: str
    days_since_review: int
    doc_url: str
    message: str


def load_registry_meta(registry_path: Path) -> list[TargetMeta]:
    """Load target metadata from registry.toml."""
    data = tomllib.loads(registry_path.read_text(encoding="utf-8"))
    metas = []
    for name, info in sorted(data.items()):
        metas.append(
            TargetMeta(
                name=name,
                doc_url=info.get("doc_url", ""),
                last_reviewed=date.fromisoformat(info["last_reviewed"]),
                status=info.get("status", "stable"),
                notes=info.get("notes", ""),
            )
        )
    return metas


def check_drift(
    metas: list[TargetMeta],
    threshold_days: int = 90,
    today: date | None = None,
) -> list[DriftWarning]:
    """Check for targets that haven't been reviewed within threshold."""
    if today is None:
        today = date.today()

    warnings = []
    for meta in metas:
        days = (today - meta.last_reviewed).days
        if days > threshold_days:
            warnings.append(
                DriftWarning(
                    target=meta.name,
                    days_since_review=days,
                    doc_url=meta.doc_url,
                    message=(
                        f"{meta.name} last reviewed {days} days ago"
                        f" (threshold: {threshold_days})"
                    ),
                )
            )
    return warnings


def format_drift_report(
    metas: list[TargetMeta], warnings: list[DriftWarning]
) -> str:
    """Format drift report for terminal."""
    lines = ["Target Platform Status:"]
    lines.append(f"{'Target':<12} {'Status':<8} {'Last Reviewed':<14} {'Notes'}")
    lines.append("-" * 70)

    warning_targets = {w.target for w in warnings}
    for meta in metas:
        flag = " !" if meta.name in warning_targets else "  "
        lines.append(
            f"{flag}{meta.name:<10} {meta.status:<8}"
            f" {meta.last_reviewed.isoformat():<14} {meta.notes}"
        )

    if warnings:
        lines.append(f"\n{len(warnings)} target(s) need review:")
        for w in warnings:
            lines.append(f"  - {w.message}")
            lines.append(f"    Docs: {w.doc_url}")
    else:
        lines.append("\nAll targets reviewed within threshold.")

    return "\n".join(lines)
