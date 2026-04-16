"""Windsurf target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class WindsurfTarget:
    """Target plugin for Windsurf (rules)."""

    @property
    def name(self) -> str:
        return "windsurf"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=(".windsurfrules",),
            supports_workflows=True,
            recommended_primary_surface="init-deep.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="windsurf",
                kind="instructions",
                relpath=f"adapters/windsurf/{cmd.id}.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        # Matches legacy render_windsurf_output(): just the body.
        return cmd.sections[0].markdown

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
