"""Tests for Continue and Roo Code target plugins."""

import unittest

from src.init_deep.ir import ArtifactIR, CommandIR, FlagIR, Intent, SectionIR
from src.init_deep.targets import TargetPlugin, create_default_registry
from src.init_deep.targets.continue_target import ContinueTarget
from src.init_deep.targets.roo import RooTarget


def _make_test_command() -> CommandIR:
    """Create a minimal CommandIR for testing."""
    return CommandIR(
        id="init-deep",
        title="Init Deep",
        summary="Analyze codebase and generate documentation",
        intent=Intent.MANUAL_WORKFLOW,
        flags=(
            FlagIR(
                name="--create-new",
                kind="bool",
                description="Create new files",
                default=True,
            ),
        ),
        sections=(
            SectionIR(
                id="main",
                kind="body",
                markdown="# Workflow\n\nDo the thing.\n",
                audience="shared",
                priority=0,
            ),
        ),
    )


class TestContinueTarget(unittest.TestCase):
    """Tests for ContinueTarget."""

    def setUp(self) -> None:
        self.target = ContinueTarget()
        self.cmd = _make_test_command()

    def test_satisfies_protocol(self) -> None:
        self.assertIsInstance(self.target, TargetPlugin)

    def test_name(self) -> None:
        self.assertEqual(self.target.name, "continue")

    def test_contract_version(self) -> None:
        self.assertEqual(self.target.contract_version, "1")

    def test_plan_produces_two_artifacts(self) -> None:
        artifacts = self.target.plan(self.cmd)
        self.assertEqual(len(artifacts), 2)

    def test_plan_artifact_kinds(self) -> None:
        artifacts = self.target.plan(self.cmd)
        kinds = {a.kind for a in artifacts}
        self.assertEqual(kinds, {"rule", "prompt"})

    def test_plan_relpaths(self) -> None:
        artifacts = self.target.plan(self.cmd)
        relpaths = {a.relpath for a in artifacts}
        self.assertEqual(
            relpaths,
            {
                "adapters/continue/rules/init-deep.md",
                "adapters/continue/prompts/init-deep.md",
            },
        )

    def test_rule_has_yaml_frontmatter(self) -> None:
        artifacts = self.target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        content = self.target.render(rule, self.cmd)
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("alwaysApply: false", content)
        self.assertIn("name: init-deep", content)
        self.assertIn("description: Analyze codebase", content)

    def test_rule_contains_body(self) -> None:
        artifacts = self.target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        content = self.target.render(rule, self.cmd)
        self.assertIn("# Workflow", content)

    def test_prompt_has_title_and_summary(self) -> None:
        artifacts = self.target.plan(self.cmd)
        prompt = [a for a in artifacts if a.kind == "prompt"][0]
        content = self.target.render(prompt, self.cmd)
        self.assertIn("# Init Deep", content)
        self.assertIn("> Analyze codebase", content)

    def test_prompt_contains_body(self) -> None:
        artifacts = self.target.plan(self.cmd)
        prompt = [a for a in artifacts if a.kind == "prompt"][0]
        content = self.target.render(prompt, self.cmd)
        self.assertIn("# Workflow", content)

    def test_validate_returns_empty_list(self) -> None:
        artifact = ArtifactIR(
            target="continue", kind="rule", relpath="test.md", content="test"
        )
        self.assertEqual(self.target.validate(artifact), [])

    def test_capabilities(self) -> None:
        caps = self.target.capabilities()
        self.assertTrue(caps.supports_commands)
        self.assertTrue(caps.supports_repo_instructions)
        self.assertFalse(caps.supports_skills)


class TestRooTarget(unittest.TestCase):
    """Tests for RooTarget."""

    def setUp(self) -> None:
        self.target = RooTarget()
        self.cmd = _make_test_command()

    def test_satisfies_protocol(self) -> None:
        self.assertIsInstance(self.target, TargetPlugin)

    def test_name(self) -> None:
        self.assertEqual(self.target.name, "roo")

    def test_contract_version(self) -> None:
        self.assertEqual(self.target.contract_version, "1")

    def test_plan_produces_two_artifacts(self) -> None:
        artifacts = self.target.plan(self.cmd)
        self.assertEqual(len(artifacts), 2)

    def test_plan_artifact_kinds(self) -> None:
        artifacts = self.target.plan(self.cmd)
        kinds = {a.kind for a in artifacts}
        self.assertEqual(kinds, {"instructions", "skill"})

    def test_plan_relpaths(self) -> None:
        artifacts = self.target.plan(self.cmd)
        relpaths = {a.relpath for a in artifacts}
        self.assertEqual(
            relpaths,
            {
                "adapters/roo/instructions/init-deep.md",
                "adapters/roo/skills/init-deep.md",
            },
        )

    def test_skill_has_yaml_frontmatter(self) -> None:
        artifacts = self.target.plan(self.cmd)
        skill = [a for a in artifacts if a.kind == "skill"][0]
        content = self.target.render(skill, self.cmd)
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("name: init-deep", content)
        self.assertIn("description: Analyze codebase", content)

    def test_skill_contains_body(self) -> None:
        artifacts = self.target.plan(self.cmd)
        skill = [a for a in artifacts if a.kind == "skill"][0]
        content = self.target.render(skill, self.cmd)
        self.assertIn("# Workflow", content)

    def test_instructions_is_plain_body(self) -> None:
        artifacts = self.target.plan(self.cmd)
        instr = [a for a in artifacts if a.kind == "instructions"][0]
        content = self.target.render(instr, self.cmd)
        self.assertEqual(content, self.cmd.sections[0].markdown)
        # No frontmatter
        self.assertFalse(content.startswith("---"))

    def test_validate_returns_empty_list(self) -> None:
        artifact = ArtifactIR(
            target="roo", kind="skill", relpath="test.md", content="test"
        )
        self.assertEqual(self.target.validate(artifact), [])

    def test_capabilities(self) -> None:
        caps = self.target.capabilities()
        self.assertTrue(caps.supports_skills)
        self.assertTrue(caps.supports_repo_instructions)


class TestRegistryWithNewTargets(unittest.TestCase):
    """Tests for registry integration of new targets."""

    def test_registry_has_nine_targets(self) -> None:
        registry = create_default_registry()
        self.assertEqual(len(registry.all()), 9)

    def test_registry_contains_continue(self) -> None:
        registry = create_default_registry()
        self.assertIsNotNone(registry.get("continue"))

    def test_registry_contains_roo(self) -> None:
        registry = create_default_registry()
        self.assertIsNotNone(registry.get("roo"))

    def test_no_relpath_collisions(self) -> None:
        registry = create_default_registry()
        cmd = _make_test_command()
        all_relpaths: list[str] = []
        for _name, plugin in registry.all().items():
            for art in plugin.plan(cmd):
                all_relpaths.append(art.relpath)
        self.assertEqual(
            len(all_relpaths),
            len(set(all_relpaths)),
            f"Duplicate relpaths: {[p for p in all_relpaths if all_relpaths.count(p) > 1]}",
        )


if __name__ == "__main__":
    unittest.main()
