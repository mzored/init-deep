"""Cursor target plugin."""

from __future__ import annotations

from textwrap import dedent

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
                relpath="adapters/cursor.mdc",
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
        # Matches legacy render_cursor_rule() exactly.
        return dedent(
            """\
            ---
            description: "Offer init-deep only when the user explicitly asks to generate or refresh agent documentation."
            alwaysApply: false
            ---

            # init-deep helper

            - Offer `/init-deep` when the user explicitly asks for a deep documentation pass.
            - The full workflow lives in `.cursor/commands/init-deep.md`.
            - Do not auto-attach the full init-deep workflow to unrelated requests.
            """
        )

    def _render_command(self, cmd: CommandIR) -> str:
        # Matches legacy render_cursor_command() exactly.
        body = cmd.sections[0].markdown
        return (
            f"# /{cmd.id}\n\n"
            "Use this command only when the user explicitly asks to initialize"
            " or refresh project agent documentation.\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
