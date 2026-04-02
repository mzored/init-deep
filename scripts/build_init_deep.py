import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.init_deep.source import load_canonical_source
from tools.init_deep.renderers import render_distribution


def managed_paths(root: Path) -> set[Path]:
    patterns = (
        "skills/init-deep/SKILL.md",
        "adapters/cursor.mdc",
        "adapters/cursor/commands/*",
        "adapters/gemini/commands/*",
        "adapters/copilot.md",
        "adapters/copilot/prompts/*",
        "adapters/windsurf/*",
        "adapters/cline/*",
    )
    paths: set[Path] = set()
    for pattern in patterns:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    return paths


def main() -> int:
    source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
    outputs = render_distribution(source)
    expected_paths = {ROOT / relative_path for relative_path in outputs}

    for stale_path in managed_paths(ROOT) - expected_paths:
        stale_path.unlink()

    for relative_path, content in outputs.items():
        destination = ROOT / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
