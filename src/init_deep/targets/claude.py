"""Claude Code target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class ClaudeTarget:
    """Target plugin for Claude Code (skills)."""

    @property
    def name(self) -> str:
        return "claude"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=("CLAUDE.md",),
            supports_skills=True,
            supports_frontmatter=True,
            recommended_primary_surface="skills/SKILL.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="claude",
                kind="skill",
                relpath=f"skills/{cmd.id}/SKILL.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        return (
            "---\n"
            f"name: {cmd.id}\n"
            f"description: {cmd.summary}. "
            f"Only invoke when user explicitly types /{cmd.id}.\n"
            f'argument-hint: "{cmd.argument_hint}"\n'
            "disable-model-invocation: true\n"
            "---\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
