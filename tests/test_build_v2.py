"""Test that new build pipeline matches legacy renderer output."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class BuildV2Tests(unittest.TestCase):
    """Verify the new registry pipeline produces byte-identical output."""

    def test_v2_matches_legacy(self) -> None:
        """The new registry pipeline must produce byte-identical output to legacy."""
        from tools.init_deep.renderers import render_distribution
        from tools.init_deep.source import load_canonical_source

        from src.init_deep.build import build_v2

        # Load via legacy
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        legacy_outputs = render_distribution(source)

        # Load via new pipeline
        v2_outputs = build_v2(ROOT / "source/commands/init-deep")

        # Legacy keys must be a subset of v2 keys (v2 may have new targets)
        self.assertTrue(
            set(legacy_outputs.keys()) <= set(v2_outputs.keys()),
            f"Legacy keys not in v2: {set(legacy_outputs.keys()) - set(v2_outputs.keys())}",
        )

        # Same content for every legacy key
        for key in sorted(legacy_outputs):
            self.assertEqual(
                legacy_outputs[key],
                v2_outputs[key],
                f"Mismatch in {key}",
            )

    def test_v2_with_selection(self) -> None:
        """Build with target selection produces only selected targets."""
        from src.init_deep.build import build_v2

        outputs = build_v2(
            ROOT / "source/commands/init-deep",
            ["claude"],
        )
        self.assertEqual(
            list(outputs.keys()),
            ["skills/init-deep/SKILL.md"],
        )

    def test_v2_unknown_target_ignored(self) -> None:
        """Unknown target names are silently skipped."""
        from src.init_deep.build import build_v2

        outputs = build_v2(
            ROOT / "source/commands/init-deep",
            ["nonexistent"],
        )
        self.assertEqual(outputs, {})

    def test_v2_multiple_targets(self) -> None:
        """Selecting multiple targets returns artifacts from each."""
        from src.init_deep.build import build_v2

        outputs = build_v2(
            ROOT / "source/commands/init-deep",
            ["claude", "cline"],
        )
        self.assertEqual(
            sorted(outputs.keys()),
            ["adapters/cline/init-deep.md", "skills/init-deep/SKILL.md"],
        )


if __name__ == "__main__":
    unittest.main()
