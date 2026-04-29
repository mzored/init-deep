from pathlib import Path
import subprocess
import unittest

from tools.init_deep.source import load_canonical_source
from tools.init_deep.renderers import render_distribution

ROOT = Path(__file__).resolve().parents[1]


class CanonicalSourceTests(unittest.TestCase):
    def test_canonical_source_declares_new_modes(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        self.assertIn("--dry-run", source.flags)
        self.assertIn("--doctor", source.flags)
        self.assertIn("--sync-check", source.flags)

    def test_canonical_source_preserves_current_workflow_depth(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        self.assertIn("## Phase 1: Discovery + Analysis (Concurrent)", source.raw)
        self.assertIn("Track ALL phases with TodoWrite.", source.raw)

    def test_canonical_source_uses_platform_neutral_search_guidance(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        self.assertIn(
            "Use the platform's native file search tools",
            source.raw,
        )
        self.assertNotIn("Use Glob and Grep tools (NOT bash find/grep)", source.raw)
        self.assertNotIn("Use Glob and Grep tools, not `find` or `grep`", source.raw)

    def test_distribution_declares_platform_native_outputs(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        self.assertIn("skills/init-deep/SKILL.md", outputs)
        self.assertTrue(outputs["skills/init-deep/SKILL.md"].startswith("---\n"))
        self.assertIn("disable-model-invocation: true", outputs["skills/init-deep/SKILL.md"])
        self.assertIn("adapters/cursor/commands/init-deep.md", outputs)
        self.assertIn("adapters/gemini/commands/init-deep.toml", outputs)
        self.assertIn("adapters/copilot/prompts/init-deep.prompt.md", outputs)
        self.assertIn("adapters/windsurf/init-deep.md", outputs)
        self.assertIn("adapters/cline/init-deep.md", outputs)


class GeneratedArtifactTests(unittest.TestCase):
    def test_rendered_artifacts_match_checked_in_files(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        for relative_path in (
            "skills/init-deep/SKILL.md",
            "adapters/cursor.mdc",
            "adapters/cursor/commands/init-deep.md",
            "adapters/copilot.md",
            "adapters/windsurf/init-deep.md",
            "adapters/cline/init-deep.md",
        ):
            actual = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertEqual(outputs[relative_path], actual, relative_path)

    def test_cursor_rule_is_not_auto_attached(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        rule = outputs["adapters/cursor.mdc"]
        self.assertIn("alwaysApply: false", rule)
        self.assertNotIn('"**/*"', rule)


class NativeCommandSurfaceTests(unittest.TestCase):
    def test_gemini_output_is_toml_command_file(self) -> None:
        import tomllib

        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        command = outputs["adapters/gemini/commands/init-deep.toml"]
        parsed = tomllib.loads(command)
        self.assertTrue(command.startswith('description = '))
        self.assertIn("prompt", parsed)
        self.assertIn(
            "Use this command only when the user explicitly asks",
            parsed["prompt"],
        )

    def test_copilot_output_is_prompt_file(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        prompt = outputs["adapters/copilot/prompts/init-deep.prompt.md"]
        self.assertTrue(prompt.startswith("# init-deep"))
        self.assertIn("Run this prompt only when the user explicitly asks", prompt)


class ModePropagationTests(unittest.TestCase):
    def test_new_modes_propagate_into_all_primary_outputs(self) -> None:
        source = load_canonical_source(ROOT / "source/init-deep/canonical.md")
        outputs = render_distribution(source)
        for flag in ("--dry-run", "--doctor", "--sync-check"):
            self.assertIn(flag, outputs["skills/init-deep/SKILL.md"])
            self.assertIn(flag, outputs["adapters/cursor/commands/init-deep.md"])
            self.assertIn(flag, outputs["adapters/gemini/commands/init-deep.toml"])
            self.assertIn(flag, outputs["adapters/copilot/prompts/init-deep.prompt.md"])
            self.assertIn(flag, outputs["adapters/windsurf/init-deep.md"])
            self.assertIn(flag, outputs["adapters/cline/init-deep.md"])


class RepositoryCheckScriptTests(unittest.TestCase):
    def test_check_script_passes_for_clean_generated_tree(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/check_init_deep.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Generated artifacts are in sync.", result.stdout)

    def test_check_script_fails_for_unexpected_generated_file(self) -> None:
        extra = ROOT / "adapters/windsurf/stale-output.md"
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text("stale\n", encoding="utf-8")
        try:
            result = subprocess.run(
                ["python3", "scripts/check_init_deep.py"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected generated artifacts", result.stdout)
        finally:
            extra.unlink()

    def test_check_script_fails_for_continue_drift(self) -> None:
        generated = ROOT / "adapters/continue/prompts/init-deep.md"
        original = generated.read_text(encoding="utf-8")
        generated.write_text(original + "\n<!-- drift -->\n", encoding="utf-8")
        try:
            result = subprocess.run(
                ["python3", "scripts/check_init_deep.py"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("adapters/continue/prompts/init-deep.md", result.stdout)
        finally:
            generated.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
