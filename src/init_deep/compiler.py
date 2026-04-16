"""Compiler: converts manifest + body into IR."""

from .ir import CommandIR, FlagIR, Intent, SectionIR
from .manifest import CommandSpec, FlagSpec


def compile_command(spec: CommandSpec, body: str) -> CommandIR:
    """Compile a CommandSpec + body text into a CommandIR."""
    flags = tuple(_compile_flag(f) for f in spec.flags)

    # For now, the entire body is a single "body" section.
    # Future: parse markdown headings to create multiple sections.
    sections = (
        SectionIR(
            id="main",
            kind="body",
            markdown=body.rstrip() + "\n",
            audience="shared",
            priority=0,
        ),
    )

    return CommandIR(
        id=spec.id,
        title=spec.title,
        summary=spec.summary,
        intent=Intent(spec.intent),
        flags=flags,
        sections=sections,
    )


def _compile_flag(flag: FlagSpec) -> FlagIR:
    return FlagIR(
        name=flag.name,
        kind=flag.kind,
        description=flag.description,
        default=flag.default,
        items=tuple(flag.items) if flag.items else (),
    )
