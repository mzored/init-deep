"""Claude Code target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities

# Hardcoded to match legacy render_skill() output exactly.
_DESCRIPTION = (
    "Deeply analyze a codebase and generate multi-agent project documentation"
    " (AGENTS.md + CLAUDE.md + GEMINI.md + scoped docs)."
    " Only invoke when user explicitly types /init-deep."
)
_ARGUMENT_HINT = (
    "[--create-new] [--max-depth=N] [--only=claude,codex]"
    " [--skip-cursor] [--dry-run] [--doctor] [--sync-check]"
)


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
            f"description: {_DESCRIPTION}\n"
            f'argument-hint: "{_ARGUMENT_HINT}"\n'
            "disable-model-invocation: true\n"
            "---\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
