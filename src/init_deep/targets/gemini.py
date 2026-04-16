"""Gemini CLI target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


def _toml_string(value: str) -> str:
    """Normalize a string for TOML triple-quoted output (matches legacy)."""
    return value.rstrip() + "\n"


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
        # Matches legacy render_gemini_command() exactly.
        body = cmd.sections[0].markdown
        prompt = (
            f"# /{cmd.id}\n\n"
            "Use this command only when the user explicitly asks to initialize"
            " or refresh project agent documentation.\n\n"
            + body
        )
        return (
            'description = "Deep project initialization for multi-agent documentation"\n\n'
            'prompt = """\n'
            + _toml_string(prompt)
            + '"""\n'
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
