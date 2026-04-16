"""Continue target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class ContinueTarget:
    """Target plugin for Continue (rules + prompts)."""

    @property
    def name(self) -> str:
        return "continue"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=("AGENTS.md",),
            supports_skills=False,
            supports_commands=True,
            supports_repo_instructions=True,
            recommended_primary_surface=".continue/rules/",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="continue",
                kind="rule",
                relpath=f"adapters/continue/rules/{cmd.id}.md",
            ),
            PlannedArtifact(
                target="continue",
                kind="prompt",
                relpath=f"adapters/continue/prompts/{cmd.id}.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        if artifact.kind == "rule":
            return (
                "---\n"
                f"name: {cmd.id}\n"
                f"description: {cmd.summary}\n"
                "globs:\n"
                "alwaysApply: false\n"
                "---\n\n"
                + body
            )
        # prompt
        return (
            f"# {cmd.title}\n\n"
            f"> {cmd.summary}\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
