"""Tests for the compatibility loader and unified loader."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CANONICAL_PATH = ROOT / "source" / "init-deep" / "canonical.md"
NEW_SOURCE_DIR = ROOT / "source" / "commands" / "init-deep"


class TestLoadLegacy(unittest.TestCase):
    """Tests for compat.load_legacy on legacy canonical.md."""

    def setUp(self):
        from src.init_deep.compat import load_legacy

        self.spec, self.body = load_legacy(CANONICAL_PATH)

    def test_produces_valid_command_spec(self):
        from src.init_deep.manifest import validate_spec

        errors = validate_spec(self.spec)
        # body_file is "(legacy)" which is intentionally non-empty
        self.assertEqual(errors, [])

    def test_has_all_six_known_flags(self):
        expected = {
            "--create-new",
            "--max-depth",
            "--only",
            "--dry-run",
            "--doctor",
            "--sync-check",
        }
        actual = {f.name for f in self.spec.flags}
        self.assertTrue(
            expected.issubset(actual),
            f"Missing flags: {expected - actual}",
        )

    def test_flag_kinds_correct(self):
        kind_map = {f.name: f.kind for f in self.spec.flags}
        self.assertEqual(kind_map["--create-new"], "bool")
        self.assertEqual(kind_map["--max-depth"], "int")
        self.assertEqual(kind_map["--only"], "csv")
        self.assertEqual(kind_map["--dry-run"], "bool")
        self.assertEqual(kind_map["--doctor"], "bool")
        self.assertEqual(kind_map["--sync-check"], "bool")

    def test_max_depth_default(self):
        for flag in self.spec.flags:
            if flag.name == "--max-depth":
                self.assertEqual(flag.default, 3)
                break

    def test_only_flag_has_items(self):
        for flag in self.spec.flags:
            if flag.name == "--only":
                self.assertGreater(len(flag.items), 0)
                self.assertIn("claude", flag.items)
                self.assertIn("cursor", flag.items)
                break

    def test_body_matches_raw_file(self):
        raw = CANONICAL_PATH.read_text(encoding="utf-8")
        self.assertEqual(self.body, raw)

    def test_legacy_source_file_set(self):
        self.assertEqual(self.spec.legacy_source_file, str(CANONICAL_PATH))

    def test_spec_metadata(self):
        self.assertEqual(self.spec.version, 1)
        self.assertEqual(self.spec.id, "init-deep")
        self.assertEqual(self.spec.title, "/init-deep")
        self.assertEqual(self.spec.intent, "manual_workflow")


class TestUnifiedLoader(unittest.TestCase):
    """Tests for loader.load_command with both formats."""

    def test_new_format_via_directory(self):
        from src.init_deep.loader import load_command

        spec, body = load_command(NEW_SOURCE_DIR)
        self.assertEqual(spec.id, "init-deep")
        self.assertEqual(spec.body_file, "body.md")
        self.assertTrue(len(body) > 0)

    def test_legacy_format_via_directory(self):
        from src.init_deep.loader import load_command

        legacy_dir = ROOT / "source" / "init-deep"
        spec, body = load_command(legacy_dir)
        self.assertEqual(spec.id, "init-deep")
        self.assertEqual(spec.body_file, "(legacy)")

    def test_legacy_format_via_direct_path(self):
        from src.init_deep.loader import load_command

        spec, body = load_command(CANONICAL_PATH)
        self.assertEqual(spec.id, "init-deep")

    def test_flag_names_match_between_formats(self):
        from src.init_deep.loader import load_command

        new_spec, _ = load_command(NEW_SOURCE_DIR)
        legacy_spec, _ = load_command(CANONICAL_PATH)

        new_names = {f.name for f in new_spec.flags}
        legacy_names = {f.name for f in legacy_spec.flags}
        # All new-format flags should appear in legacy extraction
        self.assertTrue(
            new_names.issubset(legacy_names),
            f"Flags in new format missing from legacy: {new_names - legacy_names}",
        )

    def test_body_text_identical(self):
        from src.init_deep.loader import load_command

        _, new_body = load_command(NEW_SOURCE_DIR)
        _, legacy_body = load_command(CANONICAL_PATH)
        self.assertEqual(new_body, legacy_body)

    def test_missing_source_raises(self):
        from src.init_deep.loader import load_command

        with self.assertRaises(FileNotFoundError):
            load_command(Path("/nonexistent/path"))


if __name__ == "__main__":
    unittest.main()
