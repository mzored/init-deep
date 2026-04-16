"""Copilot target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class CopilotTarget:
    """Target plugin for GitHub Copilot (instructions + prompts)."""

    @property
    def name(self) -> str:
        return "copilot"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        return TargetCapabilities(
            shared_standard_docs=(".github/copilot-instructions.md",),
            supports_repo_instructions=True,
            size_budget_bytes=8000,
            recommended_primary_surface=".github/prompts/init-deep.prompt.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        return [
            PlannedArtifact(
                target="copilot",
                kind="instructions",
                relpath="adapters/copilot.md",
            ),
            PlannedArtifact(
                target="copilot",
                kind="prompt",
                relpath=f"adapters/copilot/prompts/{cmd.id}.prompt.md",
            ),
        ]

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        if artifact.kind == "instructions":
            return self._render_instructions(cmd)
        return self._render_prompt(cmd)

    def _render_instructions(self, cmd: CommandIR) -> str:
        return (
            f"# {cmd.title}\n\n"
            f"{cmd.summary}.\n\n"
            f"For the full workflow, see `.github/prompts/{cmd.id}.prompt.md`.\n"
        )

    def _render_prompt(self, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        return (
            f"# {cmd.title}\n\n"
            f"> {cmd.summary}\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
