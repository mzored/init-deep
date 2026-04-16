"""Cursor target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class CursorTarget:
    """Target plugin for Cursor (rules + commands)."""

    @property
    def name(self) -> str:
        return "cursor"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=(".cursorrules",),
            supports_commands=True,
            supports_frontmatter=True,
            recommended_primary_surface="commands/init-deep.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="cursor",
                kind="rule",
                relpath=f"adapters/cursor.mdc",
            ),
            PlannedArtifact(
                target="cursor",
                kind="command",
                relpath=f"adapters/cursor/commands/{cmd.id}.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        if artifact.kind == "rule":
            return self._render_rule(cmd)
        return self._render_command(cmd)

    def _render_rule(self, cmd: CommandIR) -> str:
        return (
            "---\n"
            f"description: Trigger for /{cmd.id} command\n"
            "alwaysApply: false\n"
            "---\n\n"
            f"When the user types `/{cmd.id}`, follow the instructions in "
            f"`commands/{cmd.id}.md` exactly.\n"
        )

    def _render_command(self, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        return (
            f"# {cmd.title}\n\n"
            f"> {cmd.summary}\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
