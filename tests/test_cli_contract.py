"""CLI contract tests for target-scoped build/check behavior."""

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliContractTests(unittest.TestCase):
    def test_build_only_dry_run_does_not_delete_unselected_targets(self) -> None:
        result = subprocess.run(
            ["python3", "-m", "src.init_deep.cli", "build", "--only", "claude", "--dry-run"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("delete", result.stdout)
        self.assertNotIn("adapters/copilot.md", result.stdout)

    def test_check_only_diff_fails_for_selected_stale_artifact(self) -> None:
        stale = ROOT / "adapters/copilot/prompts/stale.prompt.md"
        stale.write_text("stale\n", encoding="utf-8")
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "src.init_deep.cli",
                    "check",
                    "--only",
                    "copilot",
                    "--diff",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("adapters/copilot/prompts/stale.prompt.md", result.stdout)
        finally:
            stale.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
