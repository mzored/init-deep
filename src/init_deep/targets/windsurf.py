"""Windsurf target plugin."""

from __future__ import annotations

from ..ir import ArtifactIR, CommandIR
from .base import Diagnostic, PlannedArtifact, TargetCapabilities


class WindsurfTarget:
    """Target plugin for Windsurf (rules)."""

    def __init__(self, mode: str = "legacy") -> None:
        if mode not in ("legacy", "modern"):
            raise ValueError(f"Unknown mode: {mode!r}")
        self._mode = mode

    @property
    def name(self) -> str:
        return "windsurf"

    @property
    def contract_version(self) -> str:
        return "1"

    def capabilities(self) -> TargetCapabilities:
        if self._mode == "modern":
            return TargetCapabilities(
                shared_standard_docs=(".windsurfrules",),
                supports_skills=True,
                supports_workflows=True,
                recommended_primary_surface="init-deep.md",
            )
        return TargetCapabilities(
            shared_standard_docs=(".windsurfrules",),
            supports_workflows=True,
            recommended_primary_surface="init-deep.md",
        )

    def plan(self, cmd: CommandIR) -> list[PlannedArtifact]:
        artifacts = [
            PlannedArtifact(
                target="windsurf",
                kind="instructions",
                relpath=f"adapters/windsurf/{cmd.id}.md",
            ),
        ]
        if self._mode == "modern":
            artifacts.append(
                PlannedArtifact(
                    target="windsurf",
                    kind="rule",
                    relpath=f"adapters/windsurf/rules/{cmd.id}.md",
                    metadata={"activation": "manual"},
                )
            )
        return artifacts

    def render(self, artifact: PlannedArtifact, cmd: CommandIR) -> str:
        if artifact.kind == "rule":
            return self._render_rule(cmd)
        # Matches legacy render_windsurf_output(): just the body.
        return cmd.sections[0].markdown

    def _render_rule(self, cmd: CommandIR) -> str:
        body = cmd.sections[0].markdown
        return (
            "---\n"
            f"trigger: /{cmd.id}\n"
            "activation: manual\n"
            f"description: {cmd.summary}\n"
            "---\n\n"
            + body
        )

    def validate(self, artifact: ArtifactIR) -> list[Diagnostic]:
        return []
