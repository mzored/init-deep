"""Tests for project configuration loading."""

import tempfile
import unittest
from pathlib import Path

from src.init_deep.config import ProjectConfig, default_config, load_config


class TestLoadConfig(unittest.TestCase):
    """Test loading .init-deep.toml configuration."""

    def test_missing_file_returns_defaults(self) -> None:
        path = Path("/nonexistent/.init-deep.toml")
        config = load_config(path)
        self.assertEqual(config, ProjectConfig())

    def test_default_config_values(self) -> None:
        config = default_config()
        self.assertEqual(config.version, 1)
        self.assertEqual(config.targets, ())
        self.assertEqual(config.profile, "modern")
        self.assertEqual(config.output_root, ".")
        self.assertEqual(config.commands_root, "source/commands")
        self.assertFalse(config.incremental)
        self.assertFalse(config.prune)

    def test_load_valid_toml(self) -> None:
        toml_content = """\
version = 2

[defaults]
targets = ["claude", "copilot"]
profile = "legacy"

[paths]
output_root = "dist"
commands_root = "cmds"

[behavior]
incremental = true
prune = true
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as f:
            f.write(toml_content)
            f.flush()
            config = load_config(Path(f.name))

        self.assertEqual(config.version, 2)
        self.assertEqual(config.targets, ("claude", "copilot"))
        self.assertEqual(config.profile, "legacy")
        self.assertEqual(config.output_root, "dist")
        self.assertEqual(config.commands_root, "cmds")
        self.assertTrue(config.incremental)
        self.assertTrue(config.prune)

    def test_partial_toml_uses_defaults(self) -> None:
        toml_content = """\
[defaults]
targets = ["gemini"]
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as f:
            f.write(toml_content)
            f.flush()
            config = load_config(Path(f.name))

        self.assertEqual(config.targets, ("gemini",))
        # All other fields should be defaults
        self.assertEqual(config.version, 1)
        self.assertEqual(config.profile, "modern")
        self.assertEqual(config.output_root, ".")
        self.assertFalse(config.incremental)

    def test_empty_toml_returns_defaults(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as f:
            f.write("")
            f.flush()
            config = load_config(Path(f.name))

        self.assertEqual(config, ProjectConfig())

    def test_config_is_frozen(self) -> None:
        config = default_config()
        with self.assertRaises(AttributeError):
            config.version = 99  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
