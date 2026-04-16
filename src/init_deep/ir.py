"""Intermediate representation for the init-deep compiler."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Mapping


class Intent(Enum):
    MANUAL_WORKFLOW = "manual_workflow"
    PERSISTENT_INSTRUCTION = "persistent_instruction"
    AUTO_SKILL = "auto_skill"


@dataclass(frozen=True)
class FlagIR:
    """Normalized flag representation."""

    name: str  # e.g. "--create-new"
    kind: str  # "bool", "int", "csv", "string"
    description: str
    default: Any = None
    items: tuple[str, ...] = ()

    @property
    def argument_hint(self) -> str:
        """Generate argument hint string for this flag."""
        if self.kind == "bool":
            return self.name
        if self.kind == "int":
            default = f"={self.default}" if self.default is not None else "=N"
            return f"{self.name}{default}"
        if self.kind == "csv":
            example = ",".join(self.items[:2]) if self.items else "a,b"
            return f"{self.name}={example}"
        return f"{self.name}=VALUE"


@dataclass(frozen=True)
class SectionIR:
    """A section of the command body."""

    id: str
    kind: Literal["body", "variant", "snippet"]
    markdown: str
    audience: str = "shared"  # "shared", "claude", "copilot", etc.
    priority: int = 0
    tags: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ArtifactIR:
    """A planned output artifact."""

    target: str  # e.g. "claude", "copilot"
    kind: str  # e.g. "skill", "rule", "prompt", "command", "instructions"
    relpath: str  # relative output path
    content: str  # rendered content
    metadata: Mapping[str, str] = field(
        default_factory=dict
    )  # extra metadata (e.g. source-hash)


@dataclass(frozen=True)
class CommandIR:
    """Normalized command representation — the core IR."""

    id: str
    title: str
    summary: str
    intent: Intent
    flags: tuple[FlagIR, ...]
    sections: tuple[SectionIR, ...]

    @property
    def argument_hint(self) -> str:
        """Generate combined argument hint from all flags."""
        hints = [f.argument_hint for f in self.flags]
        parts = []
        for h in hints:
            parts.append(f"[{h}]")
        return " ".join(parts)
