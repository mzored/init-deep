"""Target plugin registry."""

from __future__ import annotations

from .base import TargetPlugin


class TargetRegistry:
    """Registry of available target plugins."""

    def __init__(self) -> None:
        self._targets: dict[str, TargetPlugin] = {}

    def register(self, plugin: TargetPlugin) -> None:
        """Register a target plugin."""
        self._targets[plugin.name] = plugin

    def get(self, name: str) -> TargetPlugin | None:
        """Get a target plugin by name."""
        return self._targets.get(name)

    def list_targets(self) -> list[str]:
        """List all registered target names."""
        return sorted(self._targets.keys())

    def all(self) -> dict[str, TargetPlugin]:
        """Return all registered plugins."""
        return dict(self._targets)


def create_default_registry(profile: str = "legacy") -> TargetRegistry:
    """Create registry with all built-in targets.

    Args:
        profile: "legacy" (flat files) or "modern" (structured directories).
                 Affects Windsurf and Cline target modes.
    """
    from .claude import ClaudeTarget
    from .cline import ClineTarget
    from .copilot import CopilotTarget
    from .cursor import CursorTarget
    from .gemini import GeminiTarget
    from .windsurf import WindsurfTarget

    mode = "modern" if profile == "modern" else "legacy"

    registry = TargetRegistry()
    for target in [
        ClaudeTarget(),
        CursorTarget(),
        CopilotTarget(),
        GeminiTarget(),
        WindsurfTarget(mode=mode),
        ClineTarget(mode=mode),
    ]:
        registry.register(target)
    return registry
