"""Tests for target selection resolution."""

import unittest

from src.init_deep.selection import resolve_targets

AVAILABLE = ["claude", "cline", "copilot", "cursor", "gemini", "windsurf"]


class TestResolveTargets(unittest.TestCase):
    """Test target selection logic."""

    def test_no_flags_no_config_returns_all(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=())
        self.assertEqual(result, sorted(AVAILABLE))

    def test_config_targets_only(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=("claude", "copilot"))
        self.assertEqual(result, ["claude", "copilot"])

    def test_only_overrides_config(self) -> None:
        result = resolve_targets(
            AVAILABLE,
            config_targets=("claude", "copilot"),
            only=["gemini"],
        )
        self.assertEqual(result, ["gemini"])

    def test_skip_removes_from_all(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=(), skip=["claude", "cline"])
        self.assertNotIn("claude", result)
        self.assertNotIn("cline", result)
        self.assertEqual(result, ["copilot", "cursor", "gemini", "windsurf"])

    def test_skip_removes_from_config(self) -> None:
        result = resolve_targets(
            AVAILABLE,
            config_targets=("claude", "copilot", "gemini"),
            skip=["copilot"],
        )
        self.assertEqual(result, ["claude", "gemini"])

    def test_only_and_skip_raises(self) -> None:
        with self.assertRaises(ValueError, msg="Cannot use --only and --skip together"):
            resolve_targets(AVAILABLE, config_targets=(), only=["claude"], skip=["copilot"])

    def test_unknown_target_in_only_raises(self) -> None:
        with self.assertRaises(ValueError, msg="Unknown targets"):
            resolve_targets(AVAILABLE, config_targets=(), only=["nonexistent"])

    def test_unknown_target_in_skip_raises(self) -> None:
        with self.assertRaises(ValueError, msg="Unknown targets"):
            resolve_targets(AVAILABLE, config_targets=(), skip=["nonexistent"])

    def test_unknown_target_in_config_raises(self) -> None:
        with self.assertRaises(ValueError, msg="Unknown targets"):
            resolve_targets(AVAILABLE, config_targets=("claude", "nonexistent"))

    def test_results_are_sorted(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=(), only=["windsurf", "claude"])
        self.assertEqual(result, ["claude", "windsurf"])

    def test_only_single_target(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=(), only=["cursor"])
        self.assertEqual(result, ["cursor"])

    def test_skip_all_returns_empty(self) -> None:
        result = resolve_targets(AVAILABLE, config_targets=(), skip=AVAILABLE)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
