"""Unified source loader — handles both new and legacy formats."""

from __future__ import annotations

from pathlib import Path

from .manifest import CommandSpec, load_body, load_spec


def load_command(source_dir: Path) -> tuple[CommandSpec, str]:
    """Load a command from either new format (spec.toml) or legacy format.

    Detection logic:
    1. If source_dir / "spec.toml" exists → new format
    2. Elif source_dir is a .md file → legacy format (direct path)
    3. Elif source_dir / "canonical.md" exists → legacy format (directory)
    4. Else raise FileNotFoundError

    Returns (CommandSpec, body_text).
    """
    spec_path = source_dir / "spec.toml"
    if spec_path.exists():
        spec = load_spec(spec_path)
        body = load_body(spec, source_dir)
        return spec, body

    # Try legacy: direct .md path
    if source_dir.suffix == ".md" and source_dir.is_file():
        from .compat import load_legacy

        return load_legacy(source_dir)

    # Try legacy: directory containing canonical.md
    canonical = source_dir / "canonical.md"
    if canonical.exists():
        from .compat import load_legacy

        return load_legacy(canonical)

    raise FileNotFoundError(
        f"No spec.toml or canonical.md found in {source_dir}"
    )
