"""Base classes for target plugins."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ..ir import ArtifactIR, CommandIR


@dataclass(frozen=True)
class TargetCapabilities:
    """Declares what a target platform supports."""

    shared_standard_docs: tuple[str, ...] = ()
    supports_path_scoping: bool = False
    supports_skills: bool = False
    supports_workflows: bool = False
    supports_commands: bool = False
    supports_repo_instructions: bool = False
    size_budget_bytes: int | None = None
    supports_frontmatter: bool = False
    requires_comment_free_root: bool = False
    recommended_primary_surface: str = ""


@dataclass(frozen=True)
class Diagnostic:
    """A validation diagnostic."""

    level: str  # "error", "warning", "info"
    code: str  # e.g. "E104", "W231"
    message: str
    file: str = ""
    line: int = 0


@dataclass(frozen=True)
class PlannedArtifact:
    """An artifact planned for generation."""

    target: str
    kind: str  # "skill", "rule", "prompt", "command", "instructions"
    relpath: str
    metadata: dict[str, str] = field(default_factory=dict)


@runtime_checkable
class TargetPlugin(Protocol):
    """Protocol that all target plugins must implement."""

    @property
    def name(self) -> str: ...

    @property
    def contract_version(self) -> str: ...

    def capabilities(self) -> TargetCapabilities: ...

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]: ...

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str: ...

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]: ...
