import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.init_deep.build import build_v2
from tools.init_deep.paths import managed_paths


def main() -> int:
    outputs = build_v2(ROOT / "source/commands/init-deep")
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
