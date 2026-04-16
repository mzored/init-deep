"""Gemini CLI target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class GeminiTarget:
    """Target plugin for Gemini CLI (TOML commands)."""

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=("GEMINI.md",),
            supports_commands=True,
            recommended_primary_surface="commands/init-deep.toml",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="gemini",
                kind="command",
                relpath=f"adapters/gemini/commands/{cmd.id}.toml",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        # Escape body for TOML triple-quoted string: no escaping needed
        # for triple-quoted strings as long as there are no triple quotes in body
        return (
            f'name = "{cmd.id}"\n'
            f'description = "{cmd.summary}"\n\n'
            f"prompt = '''\n"
            f"{body}"
            f"'''\n"
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
