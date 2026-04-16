"""Compatibility loader for legacy canonical.md format."""

from __future__ import annotations

import re
from pathlib import Path

from .manifest import CommandSpec, FlagSpec

_FLAG_PATTERN = re.compile(r"`(--[^`]+)`")
# Bare flags: --flag-name (letters, digits, hyphens) anywhere in the text
_BARE_FLAG_PATTERN = re.compile(r"(--[a-z][a-z0-9-]*)")

# Known flag metadata that can't be inferred from the markdown
_KNOWN_FLAGS: dict[str, dict] = {
    "--create-new": {"kind": "bool", "description": "Regenerate docs from scratch"},
    "--max-depth": {
        "kind": "int",
        "default": 3,
        "description": "Maximum analysis depth",
    },
    "--only": {
        "kind": "csv",
        "items": (
            "claude",
            "codex",
            "gemini",
            "copilot",
            "cursor",
            "windsurf",
            "cline",
        ),
        "description": "Generate only for specified platforms",
    },
    "--dry-run": {"kind": "bool", "description": "Preview changes without writing"},
    "--doctor": {
        "kind": "bool",
        "description": "Validate workspace configuration",
    },
    "--sync-check": {
        "kind": "bool",
        "description": "Verify generated artifacts match source",
    },
}


def load_legacy(canonical_path: Path) -> tuple[CommandSpec, str]:
    """Load a legacy canonical.md and return (CommandSpec, body_text).

    The CommandSpec is inferred from the markdown content using known flag
    metadata.  The body_text is the raw content of the file.
    """
    raw = canonical_path.read_text(encoding="utf-8")

    # Extract backtick-wrapped flags (legacy parser style)
    backtick_flags = list(dict.fromkeys(_FLAG_PATTERN.findall(raw)))

    # Also extract bare flags from code blocks / plain text
    bare_flags = list(dict.fromkeys(_BARE_FLAG_PATTERN.findall(raw)))

    # Merge both sources, preserving order, deduplicating
    all_flags = list(dict.fromkeys(backtick_flags + bare_flags))

    # Build FlagSpec for each found flag
    flags: list[FlagSpec] = []
    for flag_name in all_flags:
        if flag_name in _KNOWN_FLAGS:
            meta = _KNOWN_FLAGS[flag_name]
            flags.append(
                FlagSpec(
                    name=flag_name,
                    kind=meta["kind"],
                    description=meta.get("description", ""),
                    default=meta.get("default"),
                    items=tuple(meta.get("items", ())),
                )
            )
        else:
            # Unknown flag — default to bool
            flags.append(FlagSpec(name=flag_name, kind="bool"))

    spec = CommandSpec(
        version=1,
        id="init-deep",
        title="/init-deep",
        summary="Deep project initialization for multi-assistant documentation",
        intent="manual_workflow",
        body_file="(legacy)",
        flags=tuple(flags),
        legacy_source_file=str(canonical_path),
    )

    return spec, raw
