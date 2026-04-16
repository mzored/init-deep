"""Codex target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class CodexTarget:
    """Target plugin for Codex (reads AGENTS.md natively)."""

    @property
    def name(self) -> str:
        return "codex"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=("AGENTS.md",),
            supports_skills=True,
            recommended_primary_surface="AGENTS.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return []

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        return ""

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
