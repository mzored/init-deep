"""Tests for the IR and compiler modules."""

import unittest
from pathlib import Path

from src.init_deep.compiler import compile_command, _compile_flag
from src.init_deep.ir import ArtifactIR, CommandIR, FlagIR, Intent, SectionIR
from src.init_deep.manifest import CommandSpec, FlagSpec, load_body, load_spec

SPEC_DIR = Path(__file__).resolve().parent.parent / "source" / "commands" / "init-deep"
SPEC_PATH = SPEC_DIR / "spec.toml"


class TestIntentEnum(unittest.TestCase):
    def test_manual_workflow(self):
        self.assertEqual(Intent("manual_workflow"), Intent.MANUAL_WORKFLOW)

    def test_persistent_instruction(self):
        self.assertEqual(Intent("persistent_instruction"), Intent.PERSISTENT_INSTRUCTION)

    def test_auto_skill(self):
        self.assertEqual(Intent("auto_skill"), Intent.AUTO_SKILL)

    def test_invalid_intent(self):
        with self.assertRaises(ValueError):
            Intent("bogus")


class TestFlagIR(unittest.TestCase):
    def test_bool_hint(self):
        f = FlagIR(name="--create-new", kind="bool", description="d")
        self.assertEqual(f.argument_hint, "--create-new")

    def test_int_hint_with_default(self):
        f = FlagIR(name="--max-depth", kind="int", description="d", default=3)
        self.assertEqual(f.argument_hint, "--max-depth=3")

    def test_int_hint_no_default(self):
        f = FlagIR(name="--max-depth", kind="int", description="d")
        self.assertEqual(f.argument_hint, "--max-depth=N")

    def test_csv_hint_with_items(self):
        f = FlagIR(
            name="--only",
            kind="csv",
            description="d",
            items=("claude", "codex", "gemini"),
        )
        self.assertEqual(f.argument_hint, "--only=claude,codex")

    def test_csv_hint_no_items(self):
        f = FlagIR(name="--only", kind="csv", description="d")
        self.assertEqual(f.argument_hint, "--only=a,b")

    def test_string_hint(self):
        f = FlagIR(name="--output", kind="string", description="d")
        self.assertEqual(f.argument_hint, "--output=VALUE")

    def test_frozen(self):
        f = FlagIR(name="--x", kind="bool", description="d")
        with self.assertRaises(AttributeError):
            f.name = "changed"  # type: ignore[misc]


class TestSectionIR(unittest.TestCase):
    def test_defaults(self):
        s = SectionIR(id="main", kind="body", markdown="# Hello\n")
        self.assertEqual(s.audience, "shared")
        self.assertEqual(s.priority, 0)
        self.assertEqual(s.tags, frozenset())

    def test_kind_values(self):
        for kind in ("body", "variant", "snippet"):
            s = SectionIR(id="s", kind=kind, markdown="x")
            self.assertEqual(s.kind, kind)


class TestArtifactIR(unittest.TestCase):
    def test_construction_with_metadata(self):
        a = ArtifactIR(
            target="claude",
            kind="skill",
            relpath="skills/init-deep/SKILL.md",
            content="# Skill\n",
            metadata={"source-hash": "abc123"},
        )
        self.assertEqual(a.target, "claude")
        self.assertEqual(a.metadata["source-hash"], "abc123")

    def test_default_metadata(self):
        a = ArtifactIR(target="copilot", kind="prompt", relpath="p.md", content="x")
        self.assertEqual(a.metadata, {})


class TestCommandIR(unittest.TestCase):
    def test_frozen(self):
        ir = CommandIR(
            id="test",
            title="Test",
            summary="s",
            intent=Intent.MANUAL_WORKFLOW,
            flags=(),
            sections=(),
        )
        with self.assertRaises(AttributeError):
            ir.id = "changed"  # type: ignore[misc]

    def test_argument_hint_combined(self):
        flags = (
            FlagIR(name="--create-new", kind="bool", description="d"),
            FlagIR(name="--max-depth", kind="int", description="d", default=3),
            FlagIR(
                name="--only",
                kind="csv",
                description="d",
                items=("claude", "codex"),
            ),
        )
        ir = CommandIR(
            id="test",
            title="T",
            summary="s",
            intent=Intent.MANUAL_WORKFLOW,
            flags=flags,
            sections=(),
        )
        self.assertEqual(
            ir.argument_hint,
            "[--create-new] [--max-depth=3] [--only=claude,codex]",
        )

    def test_empty_flags_hint(self):
        ir = CommandIR(
            id="test",
            title="T",
            summary="s",
            intent=Intent.MANUAL_WORKFLOW,
            flags=(),
            sections=(),
        )
        self.assertEqual(ir.argument_hint, "")


class TestCompileFromSpec(unittest.TestCase):
    """Integration test: load actual spec.toml → compile → verify IR."""

    def setUp(self):
        self.spec = load_spec(SPEC_PATH)
        self.body = load_body(self.spec, SPEC_DIR)
        self.ir = compile_command(self.spec, self.body)

    def test_id(self):
        self.assertEqual(self.ir.id, "init-deep")

    def test_title(self):
        self.assertEqual(self.ir.title, "/init-deep")

    def test_intent(self):
        self.assertEqual(self.ir.intent, Intent.MANUAL_WORKFLOW)

    def test_flag_count(self):
        self.assertEqual(len(self.ir.flags), 6)

    def test_flag_names(self):
        names = [f.name for f in self.ir.flags]
        self.assertEqual(
            names,
            [
                "--create-new",
                "--max-depth",
                "--only",
                "--dry-run",
                "--doctor",
                "--sync-check",
            ],
        )

    def test_flag_kinds(self):
        kinds = {f.name: f.kind for f in self.ir.flags}
        self.assertEqual(kinds["--create-new"], "bool")
        self.assertEqual(kinds["--max-depth"], "int")
        self.assertEqual(kinds["--only"], "csv")
        self.assertEqual(kinds["--dry-run"], "bool")

    def test_max_depth_default(self):
        flag = next(f for f in self.ir.flags if f.name == "--max-depth")
        self.assertEqual(flag.default, 3)

    def test_only_items(self):
        flag = next(f for f in self.ir.flags if f.name == "--only")
        self.assertIn("claude", flag.items)
        self.assertIn("codex", flag.items)

    def test_single_body_section(self):
        self.assertEqual(len(self.ir.sections), 1)
        section = self.ir.sections[0]
        self.assertEqual(section.id, "main")
        self.assertEqual(section.kind, "body")
        self.assertEqual(section.audience, "shared")
        self.assertTrue(section.markdown.endswith("\n"))

    def test_determinism(self):
        ir2 = compile_command(self.spec, self.body)
        self.assertEqual(self.ir, ir2)


if __name__ == "__main__":
    unittest.main()
