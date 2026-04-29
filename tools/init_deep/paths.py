"""Shared path constants and managed artifact discovery."""

from pathlib import Path

MANAGED_PATTERNS = (
    "skills/init-deep/SKILL.md",
    "adapters/cursor.mdc",
    "adapters/cursor/commands/*",
    "adapters/gemini/commands/*",
    "adapters/copilot.md",
    "adapters/copilot/prompts/*",
    "adapters/windsurf/*",
    "adapters/cline/*",
    "adapters/continue/prompts/*",
    "adapters/continue/rules/*",
    "adapters/roo/instructions/*",
    "adapters/roo/skills/*",
)


def project_root() -> Path:
    """Return the repository root based on the known package layout."""
    return Path(__file__).resolve().parents[2]


def managed_paths(root: Path) -> set[Path]:
    """Collect all generated artifact paths under *root* matching managed patterns."""
    paths: set[Path] = set()
    for pattern in MANAGED_PATTERNS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return paths
