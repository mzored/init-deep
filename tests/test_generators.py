"""Tests for metadata generators."""

import unittest

from src.init_deep.generators import (
    generate_gitattributes_entries,
    generate_managed_paths_list,
    generate_support_matrix,
    generate_target_summary,
)
from src.init_deep.targets.registry import create_default_registry


class TestSupportMatrix(unittest.TestCase):
    """Tests for generate_support_matrix."""

    def setUp(self):
        self.registry = create_default_registry()
        self.matrix = generate_support_matrix(self.registry)

    def test_produces_valid_markdown_table(self):
        lines = self.matrix.strip().split("\n")
        # Header + separator + data rows
        self.assertGreaterEqual(len(lines), 3)
        # Every line starts with |
        for line in lines:
            self.assertTrue(line.startswith("|"), f"Not a table row: {line}")

    def test_has_one_row_per_target(self):
        targets = self.registry.list_targets()
        lines = self.matrix.strip().split("\n")
        # Subtract header and separator
        data_rows = lines[2:]
        self.assertEqual(len(data_rows), len(targets))

    def test_headers_include_required_columns(self):
        header = self.matrix.split("\n")[0]
        for col in ("Platform", "Primary Surface", "Skills", "Workflows", "Commands"):
            self.assertIn(col, header)

    def test_target_count(self):
        targets = self.registry.list_targets()
        self.assertEqual(len(targets), 9)


class TestGitattributesEntries(unittest.TestCase):
    """Tests for generate_gitattributes_entries."""

    def test_produces_entries_for_all_paths(self):
        outputs = {"b/file.md": "content", "a/file.md": "content"}
        result = generate_gitattributes_entries(outputs)
        self.assertIn("a/file.md", result)
        self.assertIn("b/file.md", result)

    def test_all_entries_have_linguist_generated(self):
        outputs = {"x.md": "", "y.toml": "", "z.mdc": ""}
        result = generate_gitattributes_entries(outputs)
        for line in result.strip().split("\n"):
            if line.startswith("#"):
                continue
            self.assertIn("linguist-generated=true", line)

    def test_entries_are_sorted(self):
        outputs = {"c.md": "", "a.md": "", "b.md": ""}
        result = generate_gitattributes_entries(outputs)
        paths = [
            line.split()[0]
            for line in result.strip().split("\n")
            if not line.startswith("#")
        ]
        self.assertEqual(paths, sorted(paths))


class TestManagedPathsList(unittest.TestCase):
    """Tests for generate_managed_paths_list."""

    def test_returns_sorted_paths(self):
        outputs = {"z/a.md": "", "a/b.md": "", "m/c.md": ""}
        result = generate_managed_paths_list(outputs)
        self.assertEqual(result, ["a/b.md", "m/c.md", "z/a.md"])

    def test_empty_outputs(self):
        self.assertEqual(generate_managed_paths_list({}), [])


class TestTargetSummary(unittest.TestCase):
    """Tests for generate_target_summary."""

    def test_includes_all_target_names(self):
        registry = create_default_registry()
        summary = generate_target_summary(registry)
        for name in registry.list_targets():
            self.assertIn(name.capitalize(), summary)

    def test_includes_primary_surface(self):
        summary = generate_target_summary()
        self.assertIn("primary=", summary)

    def test_includes_shared_docs(self):
        summary = generate_target_summary()
        self.assertIn("shared_docs=", summary)


if __name__ == "__main__":
    unittest.main()
