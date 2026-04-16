"""Project-level configuration via .init-deep.toml."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectConfig:
    """Project configuration loaded from .init-deep.toml."""

    version: int = 1
    targets: tuple[str, ...] = ()  # empty = all targets
    profile: str = "modern"  # "modern" or "legacy"
    output_root: str = "."
    commands_root: str = "source/commands"
    incremental: bool = False
    prune: bool = False


def load_config(config_path: Path) -> ProjectConfig:
    """Load config from .init-deep.toml. Returns defaults if file doesn't exist."""
    if not config_path.exists():
        return ProjectConfig()

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    paths = data.get("paths", {})
    behavior = data.get("behavior", {})

    return ProjectConfig(
        version=data.get("version", 1),
        targets=tuple(defaults.get("targets", ())),
        profile=defaults.get("profile", "modern"),
        output_root=paths.get("output_root", "."),
        commands_root=paths.get("commands_root", "source/commands"),
        incremental=behavior.get("incremental", False),
        prune=behavior.get("prune", False),
    )


def default_config() -> ProjectConfig:
    """Return default config (all targets, modern profile)."""
    return ProjectConfig()
