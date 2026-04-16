"""Cline target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class ClineTarget:
    """Target plugin for Cline (rules)."""

    @property
    def name(self) -> str:
        return "cline"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=(".clinerules",),
            supports_workflows=True,
            recommended_primary_surface="init-deep.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="cline",
                kind="instructions",
                relpath=f"adapters/cline/{cmd.id}.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        return (
            f"# {cmd.title}\n\n"
            f"> {cmd.summary}\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
