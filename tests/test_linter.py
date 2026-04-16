"""Tests for the semantic linter."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from init_deep.linter import LintDiagnostic, _find_line, lint_command


class TestLintDiagnosticStr(unittest.TestCase):
    def test_with_line(self):
        d = LintDiagnostic("E001", "error", "spec.toml", 5, "bad thing")
        self.assertEqual(str(d), "E001 spec.toml:5\n  bad thing")

    def test_without_line(self):
        d = LintDiagnostic("E001", "error", "spec.toml", 0, "bad thing")
        self.assertEqual(str(d), "E001 spec.toml\n  bad thing")


class TestFindLine(unittest.TestCase):
    def test_found(self):
        text = "line one\nline two\nline three"
        self.assertEqual(_find_line(text, "two"), 2)

    def test_not_found(self):
        text = "line one\nline two"
        self.assertEqual(_find_line(text, "nope"), 0)

    def test_first_occurrence(self):
        text = "aa\nbb\naa"
        self.assertEqual(_find_line(text, "aa"), 1)


class TestLintCommandReal(unittest.TestCase):
    """Lint the actual spec dir -- should produce no errors."""

    def test_real_spec_clean(self):
        spec_dir = ROOT / "source" / "commands" / "init-deep"
        diagnostics = lint_command(spec_dir)
        errors = [d for d in diagnostics if d.severity == "error"]
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")


class TestLintMissingSpec(unittest.TestCase):
    def test_e001_missing_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            diagnostics = lint_command(Path(tmp))
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].code, "E001")
        self.assertEqual(diagnostics[0].severity, "error")


class TestLintInvalidSpec(unittest.TestCase):
    def test_e002_invalid_toml(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text("not valid [[[ toml", encoding="utf-8")
            diagnostics = lint_command(Path(tmp))
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].code, "E002")
        self.assertEqual(diagnostics[0].severity, "error")


_MINIMAL_SPEC = """\
version = 1
id = "test-cmd"
title = "Test"
summary = "A test command"
intent = "manual_workflow"

[body]
file = "body.md"

[[flags]]
name = "--verbose"
kind = "bool"
description = "Enable verbose output"

[[flags]]
name = "--only"
kind = "csv"
description = "Select targets"
items = ["claude", "cursor"]
"""


class TestLintMissingBody(unittest.TestCase):
    def test_e020_missing_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text(_MINIMAL_SPEC, encoding="utf-8")
            diagnostics = lint_command(Path(tmp))
        codes = {d.code for d in diagnostics}
        self.assertIn("E020", codes)


class TestLintFlagWarnings(unittest.TestCase):
    def test_w030_flag_in_spec_not_in_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text(_MINIMAL_SPEC, encoding="utf-8")
            body = Path(tmp) / "body.md"
            # body mentions --only but not --verbose
            body.write_text(
                "Use `--only` to select targets.\n", encoding="utf-8"
            )
            diagnostics = lint_command(Path(tmp))
        w030 = [d for d in diagnostics if d.code == "W030"]
        self.assertEqual(len(w030), 1)
        self.assertIn("--verbose", w030[0].message)

    def test_w031_flag_in_body_not_in_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text(_MINIMAL_SPEC, encoding="utf-8")
            body = Path(tmp) / "body.md"
            body.write_text(
                "Use `--verbose` and `--only` and `--unknown-flag` here.\n",
                encoding="utf-8",
            )
            diagnostics = lint_command(Path(tmp))
        w031 = [d for d in diagnostics if d.code == "W031"]
        self.assertEqual(len(w031), 1)
        self.assertIn("--unknown-flag", w031[0].message)

    def test_w031_has_line_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text(_MINIMAL_SPEC, encoding="utf-8")
            body = Path(tmp) / "body.md"
            body.write_text(
                "line one\nline two `--mystery`\nline three\n",
                encoding="utf-8",
            )
            diagnostics = lint_command(Path(tmp))
        w031 = [d for d in diagnostics if d.code == "W031"]
        self.assertTrue(len(w031) >= 1)
        mystery = [d for d in w031 if "--mystery" in d.message]
        self.assertEqual(len(mystery), 1)
        self.assertEqual(mystery[0].line, 2)


class TestLintUnknownTarget(unittest.TestCase):
    def test_w040_unknown_target_in_csv_items(self):
        spec_toml = """\
version = 1
id = "test-cmd"
title = "Test"
summary = "A test"
intent = "manual_workflow"

[body]
file = "body.md"

[[flags]]
name = "--only"
kind = "csv"
description = "Select targets"
items = ["claude", "nonexistent-platform"]
"""
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.toml"
            spec.write_text(spec_toml, encoding="utf-8")
            body = Path(tmp) / "body.md"
            body.write_text("Use `--only` to pick.\n", encoding="utf-8")
            diagnostics = lint_command(Path(tmp))
        w040 = [d for d in diagnostics if d.code == "W040"]
        self.assertEqual(len(w040), 1)
        self.assertIn("nonexistent-platform", w040[0].message)


if __name__ == "__main__":
    unittest.main()
