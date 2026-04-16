"""Manifest parser for spec.toml + body.md source format."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_VALID_INTENTS = frozenset({"manual_workflow", "persistent_instruction", "auto_skill"})
_VALID_KINDS = frozenset({"bool", "int", "csv", "string"})


@dataclass(frozen=True)
class FlagSpec:
    name: str
    kind: str
    description: str = ""
    default: Any = None
    items: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandSpec:
    version: int
    id: str
    title: str
    summary: str
    intent: str
    body_file: str
    flags: tuple[FlagSpec, ...]
    legacy_source_file: str = ""


def load_spec(spec_path: Path) -> CommandSpec:
    """Load and validate a spec.toml file."""
    text = spec_path.read_text(encoding="utf-8")
    data = tomllib.loads(text)

    # Required top-level fields
    for key in ("version", "id", "title", "summary", "intent"):
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    body_file = data.get("body", {}).get("file", "")
    if not body_file:
        raise ValueError("Missing [body] file field")

    flags: list[FlagSpec] = []
    for raw_flag in data.get("flags", []):
        flags.append(
            FlagSpec(
                name=raw_flag["name"],
                kind=raw_flag["kind"],
                description=raw_flag.get("description", ""),
                default=raw_flag.get("default"),
                items=tuple(raw_flag.get("items", [])),
            )
        )

    compat = data.get("compatibility", {})
    legacy = compat.get("legacy_source_file", "")

    return CommandSpec(
        version=data["version"],
        id=data["id"],
        title=data["title"],
        summary=data["summary"],
        intent=data["intent"],
        body_file=body_file,
        flags=tuple(flags),
        legacy_source_file=legacy,
    )


def load_body(spec: CommandSpec, spec_dir: Path) -> str:
    """Load the body markdown referenced by the spec."""
    body_path = spec_dir / spec.body_file
    return body_path.read_text(encoding="utf-8")


def validate_spec(spec: CommandSpec) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors: list[str] = []

    if spec.version != 1:
        errors.append(f"Unsupported version: {spec.version} (expected 1)")

    if not spec.id:
        errors.append("id must be non-empty")

    if not spec.title:
        errors.append("title must be non-empty")

    if not spec.summary:
        errors.append("summary must be non-empty")

    if spec.intent not in _VALID_INTENTS:
        errors.append(
            f"Unknown intent: {spec.intent!r} "
            f"(expected one of {sorted(_VALID_INTENTS)})"
        )

    if not spec.body_file:
        errors.append("body_file must be non-empty")

    # Flag validation
    seen_names: set[str] = set()
    for flag in spec.flags:
        if not flag.name.startswith("--"):
            errors.append(f"Flag name must start with '--': {flag.name!r}")

        if flag.name in seen_names:
            errors.append(f"Duplicate flag name: {flag.name!r}")
        seen_names.add(flag.name)

        if flag.kind not in _VALID_KINDS:
            errors.append(
                f"Flag {flag.name!r}: unknown kind {flag.kind!r} "
                f"(expected one of {sorted(_VALID_KINDS)})"
            )

        if flag.kind == "csv" and not flag.items:
            errors.append(
                f"Flag {flag.name!r}: csv kind should have non-empty items"
            )

    return errors
