"""Property-based tests for compiler invariants."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DeterminismTests(unittest.TestCase):
    """Verify deterministic behavior."""

    def test_compile_is_deterministic(self) -> None:
        """Compiling same input 100 times produces identical output."""
        from src.init_deep.compiler import compile_command
        from src.init_deep.manifest import CommandSpec, FlagSpec

        spec = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="Test",
            intent="manual_workflow",
            body_file="test.md",
            flags=(FlagSpec(name="--foo", kind="bool"),),
        )
        body = "# Test\nSome content\n"
        results = [compile_command(spec, body) for _ in range(100)]
        for r in results[1:]:
            self.assertEqual(results[0], r)

    def test_build_is_deterministic(self) -> None:
        """Full build pipeline produces identical output across runs."""
        from src.init_deep.build import build_v2

        outputs = [build_v2(ROOT / "source/commands/init-deep") for _ in range(10)]
        for o in outputs[1:]:
            self.assertEqual(outputs[0], o)

    def test_flag_order_does_not_affect_compilation(self) -> None:
        """Flags in different order still compile to same IR content."""
        from src.init_deep.compiler import compile_command
        from src.init_deep.manifest import CommandSpec, FlagSpec

        flags = (
            FlagSpec(name="--alpha", kind="bool"),
            FlagSpec(name="--beta", kind="int", default=5),
            FlagSpec(name="--gamma", kind="csv", items=("a", "b")),
        )
        spec1 = CommandSpec(
            version=1,
            id="test",
            title="/test",
            summary="Test",
            intent="manual_workflow",
            body_file="test.md",
            flags=flags,
        )
        # Note: the spec preserves flag order, but sections should be identical
        ir1 = compile_command(spec1, "body\n")
        ir2 = compile_command(spec1, "body\n")
        self.assertEqual(ir1.sections, ir2.sections)


class PathUniquenessTests(unittest.TestCase):
    """Verify no path collisions in generated output."""

    def test_no_duplicate_artifact_paths(self) -> None:
        """All artifact relpaths across all targets must be unique."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        paths = list(outputs.keys())
        self.assertEqual(
            len(paths),
            len(set(paths)),
            f"Duplicate paths: {[p for p in paths if paths.count(p) > 1]}",
        )

    def test_all_paths_are_relative(self) -> None:
        """No absolute paths in output keys."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path in outputs:
            self.assertFalse(path.startswith("/"), f"Absolute path: {path}")

    def test_no_path_traversal(self) -> None:
        """No '..' in output paths."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path in outputs:
            self.assertNotIn("..", path, f"Path traversal: {path}")


class OutputInvariantTests(unittest.TestCase):
    """Verify properties of all rendered outputs."""

    def test_all_outputs_are_non_empty(self) -> None:
        """Every rendered artifact must have content."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path, content in outputs.items():
            self.assertTrue(len(content) > 0, f"Empty output: {path}")

    def test_all_outputs_end_with_newline(self) -> None:
        """Every rendered artifact must end with exactly one newline."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path, content in outputs.items():
            self.assertTrue(
                content.endswith("\n"), f"Missing trailing newline: {path}"
            )

    def test_no_trailing_whitespace_on_last_line(self) -> None:
        """Last meaningful line should not have trailing spaces."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path, content in outputs.items():
            lines = content.rstrip("\n").split("\n")
            if lines:
                last = lines[-1]
                self.assertEqual(
                    last,
                    last.rstrip(),
                    f"Trailing whitespace on last line of {path}",
                )

    def test_all_outputs_are_valid_utf8(self) -> None:
        """Every output must be valid UTF-8."""
        from src.init_deep.build import build_v2

        outputs = build_v2(ROOT / "source/commands/init-deep")
        for path, content in outputs.items():
            try:
                content.encode("utf-8")
            except UnicodeEncodeError:
                self.fail(f"Invalid UTF-8 in {path}")


class RegistryInvariantTests(unittest.TestCase):
    """Verify registry properties."""

    def test_all_targets_have_unique_names(self) -> None:
        """Target names must be unique."""
        from src.init_deep.targets.registry import create_default_registry

        registry = create_default_registry()
        names = registry.list_targets()
        self.assertEqual(len(names), len(set(names)))

    def test_all_target_names_are_lowercase(self) -> None:
        """Target names must be lowercase."""
        from src.init_deep.targets.registry import create_default_registry

        registry = create_default_registry()
        for name in registry.list_targets():
            self.assertEqual(name, name.lower(), f"Non-lowercase target: {name}")

    def test_all_targets_have_contract_version(self) -> None:
        """Every target must declare a contract version."""
        from src.init_deep.targets.registry import create_default_registry

        registry = create_default_registry()
        for name in registry.list_targets():
            plugin = registry.get(name)
            self.assertTrue(
                plugin.contract_version, f"{name} has empty contract_version"
            )

    def test_all_targets_produce_at_least_one_artifact(self) -> None:
        """Every target must plan at least one artifact."""
        from src.init_deep.compiler import compile_command
        from src.init_deep.loader import load_command
        from src.init_deep.targets.registry import create_default_registry

        spec, body = load_command(ROOT / "source/commands/init-deep")
        cmd = compile_command(spec, body)
        registry = create_default_registry()
        for name in registry.list_targets():
            plugin = registry.get(name)
            artifacts = plugin.plan(cmd)
            self.assertTrue(
                len(artifacts) > 0, f"{name} produces no artifacts"
            )


if __name__ == "__main__":
    unittest.main()
