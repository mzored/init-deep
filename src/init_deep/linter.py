"""Semantic linter for init-deep source files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .manifest import CommandSpec, load_body, load_spec, validate_spec
from .targets.registry import create_default_registry


@dataclass(frozen=True)
class LintDiagnostic:
    code: str  # e.g. "E101", "W201"
    severity: str  # "error" or "warning"
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        loc = f"{self.file}:{self.line}" if self.line > 0 else self.file
        return f"{self.code} {loc}\n  {self.message}"


def lint_command(spec_dir: Path) -> list[LintDiagnostic]:
    """Lint a command source directory (containing spec.toml + body.md).

    Returns list of diagnostics (empty = clean).
    """
    diagnostics: list[LintDiagnostic] = []
    spec_path = spec_dir / "spec.toml"

    # E001: spec.toml must exist
    if not spec_path.exists():
        diagnostics.append(
            LintDiagnostic(
                code="E001",
                severity="error",
                file=str(spec_path),
                line=0,
                message="spec.toml not found",
            )
        )
        return diagnostics

    # Load and validate schema
    try:
        spec = load_spec(spec_path)
    except Exception as e:
        diagnostics.append(
            LintDiagnostic(
                code="E002",
                severity="error",
                file=str(spec_path),
                line=0,
                message=f"Failed to parse spec.toml: {e}",
            )
        )
        return diagnostics

    # E01x: Schema validation errors (from validate_spec)
    for err in validate_spec(spec):
        diagnostics.append(
            LintDiagnostic(
                code="E010",
                severity="error",
                file=str(spec_path),
                line=0,
                message=err,
            )
        )

    # E020: body file must exist
    body_path = spec_dir / spec.body_file
    if not body_path.exists():
        diagnostics.append(
            LintDiagnostic(
                code="E020",
                severity="error",
                file=str(body_path),
                line=0,
                message=f"Body file '{spec.body_file}' not found",
            )
        )
        return diagnostics

    body = load_body(spec, spec_dir)

    # W030: Flags in spec but not in body markdown
    for flag in spec.flags:
        if flag.name not in body:
            diagnostics.append(
                LintDiagnostic(
                    code="W030",
                    severity="warning",
                    file=str(body_path),
                    line=0,
                    message=f"Flag '{flag.name}' declared in spec.toml "
                    "but not found in body",
                )
            )

    # W031: Flag-like patterns in body not declared in spec
    spec_flag_names = {f.name for f in spec.flags}
    body_flags = set(re.findall(r"`(--[a-z][a-z0-9-]*)`", body))
    for bf in sorted(body_flags - spec_flag_names):
        line = _find_line(body, bf)
        diagnostics.append(
            LintDiagnostic(
                code="W031",
                severity="warning",
                file=str(body_path),
                line=line,
                message=f"Flag '{bf}' appears in body "
                "but is not declared in spec.toml",
            )
        )

    # W040: Check --only items match available targets
    registry = create_default_registry()
    available = set(registry.list_targets())
    for flag in spec.flags:
        if flag.kind == "csv" and flag.items:
            unknown_items = set(flag.items) - available
            if unknown_items:
                diagnostics.append(
                    LintDiagnostic(
                        code="W040",
                        severity="warning",
                        file=str(spec_path),
                        line=0,
                        message=f"Flag '{flag.name}' lists unknown targets: "
                        f"{', '.join(sorted(unknown_items))}",
                    )
                )

    return diagnostics


def _find_line(text: str, needle: str) -> int:
    """Find the 1-based line number of needle in text. Returns 0 if not found."""
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    return 0
