"""Snapshot tests: verify each renderer produces output identical to checked-in artifacts.

These serve as regression guards during the compiler refactor — any change to
renderer output will cause a failure, making unintended drifts immediately visible.
"""

from pathlib import Path
import unittest

from tools.init_deep.source import load_canonical_source
from tools.init_deep.renderers import (
    render_cline_output,
    render_copilot_instructions,
    render_copilot_prompt,
    render_cursor_command,
    render_cursor_rule,
    render_distribution,
    render_gemini_command,
    render_skill,
    render_windsurf_output,
)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "source/init-deep/canonical.md"

# Map each renderer to the on-disk artifact it should match.
_RENDERER_ARTIFACT_MAP: list[tuple[str, str, object]] = []  # populated in setUpModule


def setUpModule() -> None:
    """Load canonical source once for the entire module."""
    global _source
    _source = load_canonical_source(CANONICAL)


class SnapshotTests(unittest.TestCase):
    """Byte-for-byte comparison of renderer output vs checked-in files."""

    # -- individual renderer snapshots --

    def test_snapshot_skill(self) -> None:
        expected = (ROOT / "skills/init-deep/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(render_skill(_source), expected)

    def test_snapshot_cursor_rule(self) -> None:
        expected = (ROOT / "adapters/cursor.mdc").read_text(encoding="utf-8")
        self.assertEqual(render_cursor_rule(), expected)

    def test_snapshot_cursor_command(self) -> None:
        expected = (ROOT / "adapters/cursor/commands/init-deep.md").read_text(encoding="utf-8")
        self.assertEqual(render_cursor_command(_source), expected)

    def test_snapshot_copilot_instructions(self) -> None:
        expected = (ROOT / "adapters/copilot.md").read_text(encoding="utf-8")
        self.assertEqual(render_copilot_instructions(), expected)

    def test_snapshot_copilot_prompt(self) -> None:
        expected = (ROOT / "adapters/copilot/prompts/init-deep.prompt.md").read_text(encoding="utf-8")
        self.assertEqual(render_copilot_prompt(_source), expected)

    def test_snapshot_gemini_command(self) -> None:
        expected = (ROOT / "adapters/gemini/commands/init-deep.toml").read_text(encoding="utf-8")
        self.assertEqual(render_gemini_command(_source), expected)

    def test_snapshot_windsurf(self) -> None:
        expected = (ROOT / "adapters/windsurf/init-deep.md").read_text(encoding="utf-8")
        self.assertEqual(render_windsurf_output(_source), expected)

    def test_snapshot_cline(self) -> None:
        expected = (ROOT / "adapters/cline/init-deep.md").read_text(encoding="utf-8")
        self.assertEqual(render_cline_output(_source), expected)

    # -- structural tests --

    def test_distribution_returns_exactly_8_entries(self) -> None:
        outputs = render_distribution(_source)
        self.assertEqual(len(outputs), 8, f"Expected 8 entries, got {len(outputs)}: {sorted(outputs)}")

    def test_all_rendered_outputs_are_nonempty_strings(self) -> None:
        outputs = render_distribution(_source)
        for path, content in outputs.items():
            with self.subTest(path=path):
                self.assertIsInstance(content, str)
                self.assertTrue(len(content) > 0, f"{path} produced empty output")

    def test_renderers_are_deterministic(self) -> None:
        """Calling each renderer twice must produce identical output."""
        self.assertEqual(render_skill(_source), render_skill(_source))
        self.assertEqual(render_cursor_rule(), render_cursor_rule())
        self.assertEqual(render_cursor_command(_source), render_cursor_command(_source))
        self.assertEqual(render_copilot_instructions(), render_copilot_instructions())
        self.assertEqual(render_copilot_prompt(_source), render_copilot_prompt(_source))
        self.assertEqual(render_gemini_command(_source), render_gemini_command(_source))
        self.assertEqual(render_windsurf_output(_source), render_windsurf_output(_source))
        self.assertEqual(render_cline_output(_source), render_cline_output(_source))


if __name__ == "__main__":
    unittest.main()
