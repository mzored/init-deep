import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.init_deep.source import load_canonical_source
from tools.init_deep.renderers import render_distribution
from tools.init_deep.paths import managed_paths


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
