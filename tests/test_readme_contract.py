from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReadmeContractTests(unittest.TestCase):
    def test_readme_uses_platform_native_install_paths(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(".cursor/commands/init-deep.md", readme)
        self.assertIn(".gemini/commands/init-deep.toml", readme)
        self.assertIn(".github/prompts/init-deep.prompt.md", readme)
        self.assertIn("adapters/windsurf/init-deep.md", readme)
        self.assertIn("adapters/cline/init-deep.md", readme)
        self.assertIn("chat.promptFiles", readme)
        self.assertIn(".codex-plugin/plugin.json", readme)
        self.assertIn(".agents/plugins/marketplace.json", readme)
        self.assertNotIn("~/.codex/skills/init-deep", readme)
        self.assertIn("source/commands/init-deep/spec.toml", readme)
        self.assertIn("source/init-deep/canonical.md", readme)

    def test_readme_documents_new_modes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("--dry-run", readme)
        self.assertIn("--doctor", readme)
        self.assertIn("--sync-check", readme)
        self.assertNotIn("`AGENTS.md` is the canonical source of truth.", readme)


if __name__ == "__main__":
    unittest.main()
