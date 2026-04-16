import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepoMetadataTests(unittest.TestCase):
    def test_gitattributes_normalizes_text_and_marks_generated_outputs(self) -> None:
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", text)

    def test_gitattributes_only_marks_real_generated_outputs(self) -> None:
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertNotIn("adapters/* linguist-generated=true", text)
        self.assertIn("skills/init-deep/SKILL.md linguist-generated=true", text)
        self.assertIn("adapters/cursor.mdc linguist-generated=true", text)
        self.assertIn("adapters/cursor/commands/init-deep.md linguist-generated=true", text)
        self.assertIn("adapters/gemini/commands/init-deep.toml linguist-generated=true", text)
        self.assertIn("adapters/copilot/prompts/init-deep.prompt.md linguist-generated=true", text)
        self.assertIn("adapters/windsurf/init-deep.md linguist-generated=true", text)
        self.assertIn("adapters/cline/init-deep.md linguist-generated=true", text)

    def test_plugin_metadata_mentions_generated_platform_native_outputs(self) -> None:
        plugin = (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        marketplace = (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        self.assertIn("platform-native", plugin)
        self.assertIn("platform-native", marketplace)
        self.assertIn("Windsurf", plugin)
        self.assertIn("Cline", plugin)
        self.assertIn("10 AI coding platforms", marketplace)

    def test_public_repo_hygiene_files_exist(self) -> None:
        for relative_path in (
            ".editorconfig",
            ".gitignore",
            ".github/CODEOWNERS",
            ".github/CONTRIBUTING.md",
            ".github/SECURITY.md",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
        ):
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_gitignore_covers_local_state_and_python_artifacts(self) -> None:
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for expected in (
            ".DS_Store",
            ".claude/",
            ".serena/",
            "**/__pycache__/",
            "*.py[cod]",
            "*.egg-info/",
            "build/",
            "dist/",
            ".venv/",
            "docs/superpowers/",
            "*.zip",
        ):
            self.assertIn(expected, text)

    def test_contributing_documents_the_generated_artifact_workflow(self) -> None:
        text = (ROOT / ".github/CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("spec.toml", text)
        self.assertIn("body.md", text)
        self.assertIn("canonical.md", text)
        self.assertIn("python3 -m src.init_deep.cli build", text)
        self.assertIn("python3 scripts/check_init_deep.py", text)
        self.assertIn("python3 scripts/build_init_deep.py", text)
        self.assertIn("python3 -m unittest discover -s tests -v", text)

    def test_security_policy_requires_private_reports_for_sensitive_issues(self) -> None:
        text = (ROOT / ".github/SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("Do not report security vulnerabilities in public GitHub issues", text)
        self.assertIn("private vulnerability reporting", text)

    def test_codeowners_routes_reviews_to_the_repository_owner(self) -> None:
        text = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")
        self.assertIn("* @MZored", text)

    def test_marketplace_manifest_uses_supported_top_level_schema(self) -> None:
        marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("description", marketplace)
        self.assertIn("metadata", marketplace)
        self.assertEqual(
            marketplace["metadata"]["description"],
            "Canonical init-deep prompt with generated platform-native adapters for 10 AI coding platforms",
        )

    def test_plugin_and_marketplace_versions_are_synced_semver(self) -> None:
        plugin = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        marketplace = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        plugin_entry = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], plugin_entry["name"])
        self.assertEqual(plugin["version"], plugin_entry["version"])
        self.assertRegex(plugin["version"], re.compile(r"^\d+\.\d+\.\d+$"))
        self.assertEqual(plugin["repository"], "https://github.com/mzored/init-deep")

    @unittest.skipUnless(shutil.which("claude"), "claude CLI not available")
    def test_claude_cli_validates_plugin_distribution_when_available(self) -> None:
        result = subprocess.run(
            ["claude", "plugin", "validate", "."],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
