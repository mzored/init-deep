"""Copilot target plugin."""

from __future__ import annotations

from textwrap import dedent

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
        # Matches legacy render_copilot_instructions() exactly.
        return dedent(
            """\
            # init-deep repository guidance

            - Keep `.github/copilot-instructions.md` short and repository-wide.
            - Use `.github/prompts/init-deep.prompt.md` for the full init-deep workflow.
            - Treat generated `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files as outputs, not hand-maintained sources.
            """
        )

    def _render_prompt(self, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        header = (
            "# init-deep\n\n"
            "Run this prompt only when the user explicitly asks for a deep"
            " repository initialization pass.\n\n"
        )
        budget = self.capabilities().size_budget_bytes or 8000
        header_size = len(header.encode("utf-8"))
        remaining = budget - header_size
        truncation_note = (
            "\n\n<!-- Truncated to fit Copilot prompt budget. "
            "See the full workflow in the Claude Code or Cursor adapter. -->\n"
        )
        body_bytes = body.encode("utf-8")
        if len(body_bytes) > remaining:
            # Leave room for the truncation note
            cut = remaining - len(truncation_note.encode("utf-8"))
            # Truncate at last paragraph break before the cut point
            truncated = body_bytes[:cut].decode("utf-8", errors="ignore")
            last_break = truncated.rfind("\n\n")
            if last_break > 0:
                truncated = truncated[:last_break]
            return header + truncated + truncation_note
        return header + body

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
