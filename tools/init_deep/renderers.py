from __future__ import annotations

from textwrap import dedent

from .source import CanonicalSource


def _body(source: CanonicalSource) -> str:
    return source.raw.rstrip() + "\n"


def _toml_string(value: str) -> str:
    return value.rstrip() + "\n"


def render_skill(source: CanonicalSource) -> str:
    return (
        "---\n"
        "name: init-deep\n"
        "description: Deeply analyze a codebase and generate multi-agent project documentation (AGENTS.md + CLAUDE.md + GEMINI.md + scoped docs). Only invoke when user explicitly types /init-deep.\n"
        'argument-hint: "[--create-new] [--max-depth=N] [--only=claude,codex] [--skip-cursor] [--dry-run] [--doctor] [--sync-check]"\n'
        "disable-model-invocation: true\n"
        "---\n\n"
        + _body(source)
    )


def render_cursor_rule() -> str:
    return dedent(
        """\
        ---
        description: "Offer init-deep only when the user explicitly asks to generate or refresh agent documentation."
        alwaysApply: false
        ---

        # init-deep helper

        - Offer `/init-deep` when the user explicitly asks for a deep documentation pass.
        - The full workflow lives in `.cursor/commands/init-deep.md`.
        - Do not auto-attach the full init-deep workflow to unrelated requests.
        """
    )


def render_cursor_command(source: CanonicalSource) -> str:
    return (
        "# /init-deep\n\n"
        "Use this command only when the user explicitly asks to initialize or refresh project agent documentation.\n\n"
        + _body(source)
    )


def render_copilot_instructions() -> str:
    return dedent(
        """\
        # init-deep repository guidance

        - Keep `.github/copilot-instructions.md` short and repository-wide.
        - Use `.github/prompts/init-deep.prompt.md` for the full init-deep workflow.
        - Treat generated `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files as outputs, not hand-maintained sources.
        """
    )


def render_copilot_prompt(source: CanonicalSource) -> str:
    body = _body(source)
    header = (
        "# init-deep\n\n"
        "Run this prompt only when the user explicitly asks for a deep"
        " repository initialization pass.\n\n"
    )
    budget = 8000
    header_size = len(header.encode("utf-8"))
    remaining = budget - header_size
    truncation_note = (
        "\n\n<!-- Truncated to fit Copilot prompt budget. "
        "See the full workflow in the Claude Code or Cursor adapter. -->\n"
    )
    body_bytes = body.encode("utf-8")
    if len(body_bytes) > remaining:
        cut = remaining - len(truncation_note.encode("utf-8"))
        truncated = body_bytes[:cut].decode("utf-8", errors="ignore")
        last_break = truncated.rfind("\n\n")
        if last_break > 0:
            truncated = truncated[:last_break]
        return header + truncated + truncation_note
    return header + body


def render_gemini_command(source: CanonicalSource) -> str:
    prompt = (
        "# /init-deep\n\n"
        "Use this command only when the user explicitly asks to initialize or refresh project agent documentation.\n\n"
        + _body(source)
    )
    return (
        'description = "Deep project initialization for multi-agent documentation"\n\n'
        'prompt = """\n'
        + _toml_string(prompt)
        + '"""\n'
    )


def render_windsurf_output(source: CanonicalSource) -> str:
    return _body(source)


def render_cline_output(source: CanonicalSource) -> str:
    return _body(source)


def render_distribution(source: CanonicalSource) -> dict[str, str]:
    return {
        "skills/init-deep/SKILL.md": render_skill(source),
        "adapters/cursor.mdc": render_cursor_rule(),
        "adapters/cursor/commands/init-deep.md": render_cursor_command(source),
        "adapters/copilot.md": render_copilot_instructions(),
        "adapters/copilot/prompts/init-deep.prompt.md": render_copilot_prompt(source),
        "adapters/gemini/commands/init-deep.toml": render_gemini_command(source),
        "adapters/windsurf/init-deep.md": render_windsurf_output(source),
        "adapters/cline/init-deep.md": render_cline_output(source),
    }
