"""Roo Code target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class RooTarget:
    """Target plugin for Roo Code (instructions + skills)."""

    @property
    def name(self) -> str:
        return "roo"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=("AGENTS.md",),
            supports_skills=True,
            supports_repo_instructions=True,
            recommended_primary_surface=".roo/rules/",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="roo",
                kind="instructions",
                relpath=f"adapters/roo/instructions/{cmd.id}.md",
            ),
            PlannedArtifact(
                target="roo",
                kind="skill",
                relpath=f"adapters/roo/skills/{cmd.id}.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        if artifact.kind == "instructions":
            return body
        # skill
        return (
            "---\n"
            f"name: {cmd.id}\n"
            f"description: {cmd.summary}\n"
            "---\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
