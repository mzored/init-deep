"""Tests for the build planner."""

import json
import tempfile
import unittest
from pathlib import Path

from src.init_deep.planner import (
    BuildAction,
    BuildPlan,
    _infer_target,
    format_plan_json,
    format_plan_table,
    plan_build,
)


class TestPlanBuild(unittest.TestCase):
    """Tests for plan_build()."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)

    def _write(self, relpath: str, content: str) -> Path:
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_all_unchanged(self) -> None:
        self._write("skills/init-deep/SKILL.md", "hello")
        outputs = {"skills/init-deep/SKILL.md": "hello"}
        plan = plan_build(outputs, self.root, managed=set())
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].op, "skip")
        self.assertEqual(plan.actions[0].status, "unchanged")

    def test_changed_file(self) -> None:
        self._write("skills/init-deep/SKILL.md", "old content")
        outputs = {"skills/init-deep/SKILL.md": "new content"}
        plan = plan_build(outputs, self.root, managed=set())
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].op, "write")
        self.assertEqual(plan.actions[0].status, "changed")

    def test_new_file(self) -> None:
        outputs = {"adapters/copilot.md": "content"}
        plan = plan_build(outputs, self.root, managed=set())
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].op, "write")
        self.assertEqual(plan.actions[0].status, "new")

    def test_stale_file_with_prune(self) -> None:
        stale_path = self._write("adapters/old.md", "stale")
        plan = plan_build({}, self.root, managed={stale_path}, prune=True)
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].op, "delete")
        self.assertEqual(plan.actions[0].status, "stale")

    def test_stale_file_without_prune(self) -> None:
        stale_path = self._write("adapters/old.md", "stale")
        plan = plan_build({}, self.root, managed={stale_path}, prune=False)
        self.assertEqual(len(plan.actions), 1)
        self.assertEqual(plan.actions[0].op, "skip")
        self.assertEqual(plan.actions[0].status, "stale")

    def test_plan_properties(self) -> None:
        self._write("skills/init-deep/SKILL.md", "same")
        self._write("adapters/copilot.md", "old")
        stale = self._write("adapters/old.md", "stale")
        outputs = {
            "skills/init-deep/SKILL.md": "same",
            "adapters/copilot.md": "new",
        }
        plan = plan_build(outputs, self.root, managed={stale}, prune=True)
        self.assertEqual(len(plan.writes), 1)
        self.assertEqual(len(plan.skips), 1)
        self.assertEqual(len(plan.deletes), 1)


class TestFormatPlanTable(unittest.TestCase):
    """Tests for format_plan_table()."""

    def test_empty_plan(self) -> None:
        plan = BuildPlan(actions=[])
        self.assertEqual(format_plan_table(plan), "No actions needed.")

    def test_table_output(self) -> None:
        plan = BuildPlan(actions=[
            BuildAction("write", "claude", "skills/SKILL.md", "changed", "content differs"),
        ])
        table = format_plan_table(plan)
        self.assertIn("Op", table)
        self.assertIn("write", table)
        self.assertIn("claude", table)
        self.assertIn("changed", table)


class TestFormatPlanJson(unittest.TestCase):
    """Tests for format_plan_json()."""

    def test_valid_json(self) -> None:
        plan = BuildPlan(actions=[
            BuildAction("write", "claude", "skills/SKILL.md", "changed", "content differs"),
            BuildAction("skip", "copilot", "adapters/copilot.md", "unchanged", "content matches"),
        ])
        result = format_plan_json(plan)
        data = json.loads(result)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["op"], "write")
        self.assertEqual(data[1]["status"], "unchanged")


class TestInferTarget(unittest.TestCase):
    """Tests for _infer_target()."""

    def test_cursor(self) -> None:
        self.assertEqual(_infer_target("adapters/cursor/commands/init-deep.md"), "cursor")

    def test_copilot(self) -> None:
        self.assertEqual(_infer_target("adapters/copilot.md"), "copilot")

    def test_gemini(self) -> None:
        self.assertEqual(_infer_target("adapters/gemini/commands/init-deep.toml"), "gemini")

    def test_windsurf(self) -> None:
        self.assertEqual(_infer_target("adapters/windsurf/init-deep.md"), "windsurf")

    def test_cline(self) -> None:
        self.assertEqual(_infer_target("adapters/cline/init-deep.md"), "cline")

    def test_claude_skill(self) -> None:
        self.assertEqual(_infer_target("skills/init-deep/SKILL.md"), "claude")

    def test_unknown(self) -> None:
        self.assertEqual(_infer_target("something/else.txt"), "unknown")


if __name__ == "__main__":
    unittest.main()
