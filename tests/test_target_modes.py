"""Tests for Windsurf and Cline legacy/modern mode support."""

import unittest

from src.init_deep.ir import CommandIR, FlagIR, Intent, SectionIR
from src.init_deep.targets import create_default_registry
from src.init_deep.targets.cline import ClineTarget
from src.init_deep.targets.windsurf import WindsurfTarget


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


class TestWindsurfModes(unittest.TestCase):
    """Tests for WindsurfTarget mode support."""

    def setUp(self) -> None:
        self.cmd = _make_test_command()

    def test_legacy_produces_one_artifact(self) -> None:
        target = WindsurfTarget("legacy")
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].kind, "instructions")

    def test_modern_produces_two_artifacts(self) -> None:
        target = WindsurfTarget("modern")
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 2)
        kinds = {a.kind for a in artifacts}
        self.assertEqual(kinds, {"instructions", "rule"})

    def test_legacy_body_matches_current_output(self) -> None:
        target = WindsurfTarget("legacy")
        artifacts = target.plan(self.cmd)
        content = target.render(artifacts[0], self.cmd)
        self.assertEqual(content, self.cmd.sections[0].markdown)

    def test_modern_rule_has_frontmatter(self) -> None:
        target = WindsurfTarget("modern")
        artifacts = target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        content = target.render(rule, self.cmd)
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("trigger: /init-deep", content)
        self.assertIn("activation: manual", content)
        self.assertIn("description: Analyze codebase", content)
        # Body appears after frontmatter
        self.assertIn("# Workflow", content)

    def test_modern_instructions_same_as_legacy(self) -> None:
        legacy = WindsurfTarget("legacy")
        modern = WindsurfTarget("modern")
        legacy_arts = legacy.plan(self.cmd)
        modern_arts = modern.plan(self.cmd)
        instr_legacy = legacy.render(legacy_arts[0], self.cmd)
        instr_modern = modern.render(
            [a for a in modern_arts if a.kind == "instructions"][0], self.cmd
        )
        self.assertEqual(instr_legacy, instr_modern)

    def test_default_mode_is_legacy(self) -> None:
        target = WindsurfTarget()
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 1)

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            WindsurfTarget("invalid")

    def test_modern_capabilities_support_skills(self) -> None:
        target = WindsurfTarget("modern")
        caps = target.capabilities()
        self.assertTrue(caps.supports_skills)
        self.assertTrue(caps.supports_workflows)

    def test_legacy_capabilities_no_skills(self) -> None:
        target = WindsurfTarget("legacy")
        caps = target.capabilities()
        self.assertFalse(caps.supports_skills)

    def test_modern_rule_relpath(self) -> None:
        target = WindsurfTarget("modern")
        artifacts = target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        self.assertEqual(rule.relpath, "adapters/windsurf/rules/init-deep.md")

    def test_modern_rule_metadata(self) -> None:
        target = WindsurfTarget("modern")
        artifacts = target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        self.assertEqual(rule.metadata, {"activation": "manual"})


class TestClineModes(unittest.TestCase):
    """Tests for ClineTarget mode support."""

    def setUp(self) -> None:
        self.cmd = _make_test_command()

    def test_legacy_produces_one_artifact(self) -> None:
        target = ClineTarget("legacy")
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].kind, "instructions")

    def test_modern_produces_two_artifacts(self) -> None:
        target = ClineTarget("modern")
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 2)
        kinds = {a.kind for a in artifacts}
        self.assertEqual(kinds, {"instructions", "rule"})

    def test_legacy_body_matches_current_output(self) -> None:
        target = ClineTarget("legacy")
        artifacts = target.plan(self.cmd)
        content = target.render(artifacts[0], self.cmd)
        self.assertEqual(content, self.cmd.sections[0].markdown)

    def test_modern_rule_has_frontmatter(self) -> None:
        target = ClineTarget("modern")
        artifacts = target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        content = target.render(rule, self.cmd)
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("trigger: /init-deep", content)
        self.assertIn("activation: manual", content)
        self.assertIn("description: Analyze codebase", content)
        self.assertIn("# Workflow", content)

    def test_modern_instructions_same_as_legacy(self) -> None:
        legacy = ClineTarget("legacy")
        modern = ClineTarget("modern")
        legacy_arts = legacy.plan(self.cmd)
        modern_arts = modern.plan(self.cmd)
        instr_legacy = legacy.render(legacy_arts[0], self.cmd)
        instr_modern = modern.render(
            [a for a in modern_arts if a.kind == "instructions"][0], self.cmd
        )
        self.assertEqual(instr_legacy, instr_modern)

    def test_default_mode_is_legacy(self) -> None:
        target = ClineTarget()
        artifacts = target.plan(self.cmd)
        self.assertEqual(len(artifacts), 1)

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            ClineTarget("invalid")

    def test_modern_capabilities_support_skills(self) -> None:
        target = ClineTarget("modern")
        caps = target.capabilities()
        self.assertTrue(caps.supports_skills)
        self.assertTrue(caps.supports_workflows)

    def test_legacy_capabilities_no_skills(self) -> None:
        target = ClineTarget("legacy")
        caps = target.capabilities()
        self.assertFalse(caps.supports_skills)

    def test_modern_rule_relpath(self) -> None:
        target = ClineTarget("modern")
        artifacts = target.plan(self.cmd)
        rule = [a for a in artifacts if a.kind == "rule"][0]
        self.assertEqual(rule.relpath, "adapters/cline/rules/init-deep.md")


class TestRegistryModes(unittest.TestCase):
    """Tests for registry profile parameter."""

    def test_default_registry_uses_legacy(self) -> None:
        registry = create_default_registry()
        windsurf = registry.get("windsurf")
        cline = registry.get("cline")
        assert windsurf is not None and cline is not None
        self.assertFalse(windsurf.capabilities().supports_skills)
        self.assertFalse(cline.capabilities().supports_skills)

    def test_legacy_registry_explicit(self) -> None:
        registry = create_default_registry("legacy")
        windsurf = registry.get("windsurf")
        cline = registry.get("cline")
        assert windsurf is not None and cline is not None
        self.assertFalse(windsurf.capabilities().supports_skills)
        self.assertFalse(cline.capabilities().supports_skills)

    def test_modern_registry(self) -> None:
        registry = create_default_registry("modern")
        windsurf = registry.get("windsurf")
        cline = registry.get("cline")
        assert windsurf is not None and cline is not None
        self.assertTrue(windsurf.capabilities().supports_skills)
        self.assertTrue(cline.capabilities().supports_skills)

    def test_modern_registry_artifact_count(self) -> None:
        cmd = _make_test_command()
        registry = create_default_registry("modern")
        windsurf = registry.get("windsurf")
        cline = registry.get("cline")
        assert windsurf is not None and cline is not None
        self.assertEqual(len(windsurf.plan(cmd)), 2)
        self.assertEqual(len(cline.plan(cmd)), 2)

    def test_legacy_registry_artifact_count(self) -> None:
        cmd = _make_test_command()
        registry = create_default_registry("legacy")
        windsurf = registry.get("windsurf")
        cline = registry.get("cline")
        assert windsurf is not None and cline is not None
        self.assertEqual(len(windsurf.plan(cmd)), 1)
        self.assertEqual(len(cline.plan(cmd)), 1)

    def test_modern_does_not_affect_other_targets(self) -> None:
        registry = create_default_registry("modern")
        claude = registry.get("claude")
        assert claude is not None
        cmd = _make_test_command()
        # Claude should be unaffected by profile
        artifacts = claude.plan(cmd)
        self.assertGreater(len(artifacts), 0)


if __name__ == "__main__":
    unittest.main()
