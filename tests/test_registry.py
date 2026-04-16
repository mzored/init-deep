"""Tests for the target plugin registry and plugin protocol."""

import unittest

from src.init_deep.ir import CommandIR, FlagIR, Intent, SectionIR
from src.init_deep.targets import (
    TargetPlugin,
    TargetRegistry,
    create_default_registry,
)
from src.init_deep.targets.base import PlannedArtifact


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
            FlagIR(
                name="--depth",
                kind="int",
                description="Analysis depth",
                default=3,
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


class TestTargetRegistry(unittest.TestCase):
    """Tests for TargetRegistry."""

    def test_register_and_get(self) -> None:
        registry = TargetRegistry()
        default = create_default_registry()
        claude = default.get("claude")
        assert claude is not None
        registry.register(claude)
        self.assertIs(registry.get("claude"), claude)

    def test_get_missing_returns_none(self) -> None:
        registry = TargetRegistry()
        self.assertIsNone(registry.get("nonexistent"))

    def test_list_targets_sorted(self) -> None:
        registry = create_default_registry()
        names = registry.list_targets()
        self.assertEqual(names, sorted(names))

    def test_all_returns_copy(self) -> None:
        registry = create_default_registry()
        all_targets = registry.all()
        self.assertIsInstance(all_targets, dict)
        self.assertEqual(len(all_targets), 6)


class TestDefaultRegistry(unittest.TestCase):
    """Tests for the default registry contents."""

    EXPECTED_TARGETS = ["claude", "cline", "copilot", "cursor", "gemini", "windsurf"]

    def setUp(self) -> None:
        self.registry = create_default_registry()

    def test_has_all_six_targets(self) -> None:
        self.assertEqual(self.registry.list_targets(), self.EXPECTED_TARGETS)

    def test_all_names_lowercase(self) -> None:
        for name in self.registry.list_targets():
            self.assertEqual(name, name.lower(), f"Target name {name!r} is not lowercase")

    def test_all_satisfy_protocol(self) -> None:
        for name, plugin in self.registry.all().items():
            self.assertIsInstance(
                plugin,
                TargetPlugin,
                f"{name} does not satisfy TargetPlugin protocol",
            )


class TestTargetPlugins(unittest.TestCase):
    """Tests for individual target plugin behavior."""

    def setUp(self) -> None:
        self.registry = create_default_registry()
        self.cmd = _make_test_command()

    def test_each_target_can_plan(self) -> None:
        for name, plugin in self.registry.all().items():
            artifacts = plugin.plan(self.cmd)
            self.assertIsInstance(artifacts, list, f"{name}.plan() must return a list")
            self.assertGreater(len(artifacts), 0, f"{name}.plan() returned empty list")
            for art in artifacts:
                self.assertIsInstance(art, PlannedArtifact)
                self.assertEqual(art.target, name)

    def test_each_target_can_render(self) -> None:
        for name, plugin in self.registry.all().items():
            artifacts = plugin.plan(self.cmd)
            for art in artifacts:
                content = plugin.render(art, self.cmd)
                self.assertIsInstance(content, str, f"{name}.render() must return str")
                self.assertGreater(
                    len(content), 0, f"{name}.render() returned empty string"
                )

    def test_no_duplicate_relpaths_across_targets(self) -> None:
        all_relpaths: list[str] = []
        for _name, plugin in self.registry.all().items():
            artifacts = plugin.plan(self.cmd)
            for art in artifacts:
                all_relpaths.append(art.relpath)
        self.assertEqual(
            len(all_relpaths),
            len(set(all_relpaths)),
            f"Duplicate relpaths found: {all_relpaths}",
        )

    def test_contract_version_nonempty(self) -> None:
        for name, plugin in self.registry.all().items():
            self.assertTrue(
                plugin.contract_version,
                f"{name}.contract_version is empty",
            )

    def test_capabilities_returns_dataclass(self) -> None:
        from src.init_deep.targets.base import TargetCapabilities

        for name, plugin in self.registry.all().items():
            caps = plugin.capabilities()
            self.assertIsInstance(caps, TargetCapabilities, f"{name}.capabilities()")

    def test_validate_returns_list(self) -> None:
        from src.init_deep.ir import ArtifactIR

        artifact = ArtifactIR(
            target="test", kind="skill", relpath="test.md", content="test"
        )
        for name, plugin in self.registry.all().items():
            result = plugin.validate(artifact)
            self.assertIsInstance(result, list, f"{name}.validate()")


if __name__ == "__main__":
    unittest.main()
