import sys
from difflib import unified_diff
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.init_deep.source import load_canonical_source
from tools.init_deep.renderers import render_distribution
from tools.init_deep.paths import managed_paths


def main() -> int:
    source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
    expected_outputs = render_distribution(source)
    mismatches: list[str] = []
    expected_paths = {ROOT / relative_path for relative_path in expected_outputs}

    for relative_path, expected in expected_outputs.items():
        path = ROOT / relative_path
        actual = path.read_text(encoding="utf-8") if path.exists() else ""
        if actual != expected:
            mismatches.append(
                "".join(
                    unified_diff(
                        actual.splitlines(keepends=True),
                        expected.splitlines(keepends=True),
                        fromfile=str(path),
                        tofile=f"{path} (generated)",
                    )
                )
            )

    unexpected_paths = sorted(managed_paths(ROOT) - expected_paths)
    if unexpected_paths:
        mismatches.append(
            "Unexpected generated artifacts:\n"
            + "\n".join(str(path.relative_to(ROOT)) for path in unexpected_paths)
        )

    if mismatches:
        print("Generated artifacts are out of sync.\n")
        print("\n".join(mismatches))
        return 1

    print("Generated artifacts are in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
