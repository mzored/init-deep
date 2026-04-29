# AGENTS.md

## Overview

Multi-platform AI documentation generator. It analyzes codebases and produces platform-native docs so AI coding assistants understand the project. Built with Python 3.11+ and the standard library only.

## Setup

```bash
python3 --version   # requires 3.11+
node --version      # required only for markdownlint
```

No install step is required for local development.

## Commands

```bash
# Build: regenerate all platform adapters from source/commands/init-deep
python3 scripts/build_init_deep.py

# Validate: check checked-in generated artifacts match source
python3 scripts/check_init_deep.py
python3 -m src.init_deep.cli check

# Lint/doctor source metadata
python3 -m src.init_deep.cli lint
python3 -m src.init_deep.cli doctor

# Test
python3 -m unittest discover -s tests -v

# Lint markdown
npx -y markdownlint-cli2 "README.md" "skills/**/*.md" "adapters/**/*.md" "adapters/**/*.mdc"

# Validate configs
python3 -c "from pathlib import Path; import tomllib; tomllib.loads(Path('adapters/gemini/commands/init-deep.toml').read_text(encoding='utf-8'))"
jq . .claude-plugin/plugin.json > /dev/null
jq . .claude-plugin/marketplace.json > /dev/null
jq . .codex-plugin/plugin.json > /dev/null
jq . .agents/plugins/marketplace.json > /dev/null

# Full CI locally
python3 scripts/check_init_deep.py && python3 scripts/build_init_deep.py && git diff --exit-code && python3 -m src.init_deep.cli check && python3 -m unittest discover -s tests -v
```

## Architecture

Primary pipeline:

```
source/commands/init-deep/spec.toml    # typed manifest: flags, metadata, intent
source/commands/init-deep/body.md      # markdown workflow body
    |
    v
src/init_deep/manifest.py              # spec.toml -> CommandSpec
src/init_deep/compiler.py              # CommandSpec + body -> CommandIR
src/init_deep/targets/registry.py      # registry with 9 built-in targets
src/init_deep/targets/                 # target plugins: plan() + render()
    |
    v
src/init_deep/build.py                 # build_v2(): renders artifacts
scripts/build_init_deep.py             # writes generated artifacts
scripts/check_init_deep.py             # byte-for-byte sync validation
```

Legacy compatibility:

```
source/init-deep/canonical.md          # legacy single-file source kept in sync
tools/init_deep/source.py              # CanonicalSource parser
tools/init_deep/renderers.py           # legacy renderer snapshots
tools/init_deep/paths.py               # managed generated artifact paths
```

Generated/distribution files:

```
skills/init-deep/SKILL.md              # Claude Code / Agent Skills workflow
adapters/cursor.mdc                    # Cursor trigger rule
adapters/cursor/commands/init-deep.md  # Cursor full command
adapters/copilot.md                    # Copilot short repo instructions
adapters/copilot/prompts/*.prompt.md   # Copilot prompt
adapters/gemini/commands/*.toml        # Gemini CLI command
adapters/windsurf/init-deep.md         # Windsurf adapter
adapters/cline/init-deep.md            # Cline adapter
adapters/continue/                     # Continue rules + prompt
adapters/roo/                          # Roo Code instructions + skill
.claude-plugin/                        # Claude Code plugin metadata
.codex-plugin/                         # Codex plugin metadata
.agents/plugins/marketplace.json       # Codex repo marketplace
```

## Conventions

- Edit `source/commands/init-deep/spec.toml` and `source/commands/init-deep/body.md` for workflow changes.
- Keep `source/init-deep/canonical.md` byte-identical to `body.md` until legacy compatibility is removed.
- Do not hand-edit generated artifacts in `skills/` or `adapters/`; rebuild them.
- Target plugins live in `src/init_deep/targets/` and implement `plan()`, `render()`, and `validate()`.
- Frozen dataclasses (`CommandSpec`, `CommandIR`, `SectionIR`, `ArtifactIR`) are the cross-target contract.
- Tests are integration-style and read real files from disk.
- `.gitattributes` marks generated outputs with `linguist-generated=true`.

## Known Pitfalls

- `scripts/build_init_deep.py` and `scripts/check_init_deep.py` must cover every registry-generated artifact, including Continue and Roo.
- `textwrap.dedent` fails with f-string interpolation when the body lacks common indentation; use plain string concatenation in renderers.
- Cursor `.mdc` uses `alwaysApply: false`; the full workflow lives in `adapters/cursor/commands/init-deep.md`.
- Copilot prompt output is budget-truncated; do not describe it as the complete workflow.
- Gemini adapter is TOML, not Markdown; validate it with `tomllib`.
- Roo Code is scheduled to shut down on May 15, 2026; keep Roo support for existing users only unless that upstream status changes.
