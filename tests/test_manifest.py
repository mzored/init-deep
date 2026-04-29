"""Tests for spec.toml + body.md manifest parser."""

import unittest
from pathlib import Path

from src.init_deep.manifest import (
    CommandSpec,
    FlagSpec,
    load_body,
    load_spec,
    validate_spec,
)

ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "source" / "commands" / "init-deep"
SPEC_PATH = SPEC_DIR / "spec.toml"
CANONICAL_PATH = ROOT / "source" / "init-deep" / "canonical.md"


class TestLoadSpec(unittest.TestCase):
    """Test loading the actual spec.toml from disk."""

    def setUp(self):
        self.spec = load_spec(SPEC_PATH)

    def test_top_level_fields(self):
        self.assertEqual(self.spec.version, 1)
        self.assertEqual(self.spec.id, "init-deep")
        self.assertEqual(self.spec.title, "/init-deep")
        self.assertEqual(self.spec.summary, "Deep project initialization for multi-assistant documentation")
        self.assertEqual(self.spec.intent, "manual_workflow")

    def test_body_file(self):
        self.assertEqual(self.spec.body_file, "body.md")

    def test_flags_count(self):
        self.assertEqual(len(self.spec.flags), 6)

    def test_flag_names(self):
        expected = {
            "--create-new",
            "--max-depth",
            "--only",
            "--dry-run",
            "--doctor",
            "--sync-check",
        }
        actual = {f.name for f in self.spec.flags}
        self.assertEqual(actual, expected)

    def test_flag_kinds(self):
        kinds = {f.name: f.kind for f in self.spec.flags}
        self.assertEqual(kinds["--create-new"], "bool")
        self.assertEqual(kinds["--max-depth"], "int")
        self.assertEqual(kinds["--only"], "csv")
        self.assertEqual(kinds["--dry-run"], "bool")
        self.assertEqual(kinds["--doctor"], "bool")
        self.assertEqual(kinds["--sync-check"], "bool")

    def test_csv_flag_has_items(self):
        only_flag = next(f for f in self.spec.flags if f.name == "--only")
        self.assertIn("claude", only_flag.items)
        self.assertIn("cursor", only_flag.items)
        self.assertIn("continue", only_flag.items)
        self.assertIn("roo", only_flag.items)
        self.assertEqual(len(only_flag.items), 9)

    def test_int_flag_has_default(self):
        max_depth = next(f for f in self.spec.flags if f.name == "--max-depth")
        self.assertEqual(max_depth.default, 3)

    def test_legacy_source_file(self):
        self.assertEqual(self.spec.legacy_source_file, "source/init-deep/canonical.md")

    def test_frozen(self):
        with self.assertRaises(AttributeError):
            self.spec.id = "other"


class TestLoadBody(unittest.TestCase):
    """Test loading the body.md file."""

    def setUp(self):
        self.spec = load_spec(SPEC_PATH)

    def test_body_loads_and_nonempty(self):
        body = load_body(self.spec, SPEC_DIR)
        self.assertIsInstance(body, str)
        self.assertTrue(len(body) > 0)

    def test_body_matches_canonical(self):
        body = load_body(self.spec, SPEC_DIR)
        canonical = CANONICAL_PATH.read_text(encoding="utf-8")
        self.assertEqual(body, canonical)


class TestValidateSpec(unittest.TestCase):
    """Test validate_spec with both valid and invalid specs."""

    def test_valid_spec_no_errors(self):
        spec = load_spec(SPEC_PATH)
        errors = validate_spec(spec)
        self.assertEqual(errors, [])

    def test_missing_id(self):
        spec = CommandSpec(
            version=1,
            id="",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("id must be non-empty" in e for e in errors))

    def test_unknown_intent(self):
        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="test",
            intent="unknown_intent",
            body_file="body.md",
            flags=(),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("Unknown intent" in e for e in errors))

    def test_duplicate_flags(self):
        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(
                FlagSpec(name="--foo", kind="bool"),
                FlagSpec(name="--foo", kind="int"),
            ),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("Duplicate flag" in e for e in errors))

    def test_invalid_flag_name(self):
        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(FlagSpec(name="no-dashes", kind="bool"),),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("must start with '--'" in e for e in errors))

    def test_unknown_flag_kind(self):
        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(FlagSpec(name="--foo", kind="float"),),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("unknown kind" in e for e in errors))

    def test_csv_without_items(self):
        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(FlagSpec(name="--foo", kind="csv"),),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("csv kind should have non-empty items" in e for e in errors))

    def test_unsupported_version(self):
        spec = CommandSpec(
            version=99,
            id="test",
            title="/test",
            summary="test",
            intent="manual_workflow",
            body_file="body.md",
            flags=(),
        )
        errors = validate_spec(spec)
        self.assertTrue(any("Unsupported version" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
