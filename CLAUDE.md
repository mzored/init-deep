# CLAUDE.md

## Overview

Multi-platform AI documentation generator. Analyzes codebases and produces platform-native docs so every AI coding assistant understands the project. Built with Python 3.11, no external dependencies.

## Setup

```bash
python3 --version   # requires 3.11+
node --version      # required only for markdownlint
```

No install step — pure stdlib Python.

## Commands

```bash
# Build: regenerate all platform adapters (new CLI)
python3 -m src.init_deep.cli build

# Validate: check generated artifacts match source
python3 -m src.init_deep.cli check

# Lint: validate source schema and semantics
python3 -m src.init_deep.cli lint

# Doctor: check workspace health
python3 -m src.init_deep.cli doctor

# Build with preview modes
python3 -m src.init_deep.cli build --dry-run
python3 -m src.init_deep.cli build --diff
python3 -m src.init_deep.cli build --json

# Legacy build/check scripts (still functional)
python3 scripts/build_init_deep.py
python3 scripts/check_init_deep.py

# Test
python3 -m unittest discover -s tests -v

# Lint markdown
npx -y markdownlint-cli2 "README.md" "skills/**/*.md" "adapters/**/*.md" "adapters/**/*.mdc"

# Validate configs
python3 -c "from pathlib import Path; import tomllib; tomllib.loads(Path('adapters/gemini/commands/init-deep.toml').read_text(encoding='utf-8'))"
jq . .claude-plugin/plugin.json > /dev/null
jq . .claude-plugin/marketplace.json > /dev/null

# Full CI locally
python3 scripts/check_init_deep.py && python3 scripts/build_init_deep.py && git diff --exit-code && python3 -m unittest discover -s tests -v
```

## Architecture

The project has two layers: a legacy compatibility layer and the new typed compiler.

### New compiler pipeline (primary)

```
source/commands/init-deep/spec.toml    # Typed manifest (flags, metadata)
source/commands/init-deep/body.md      # Markdown body (instructions)
    |
    v
src/init_deep/manifest.py             # Parses spec.toml → CommandSpec
src/init_deep/compiler.py             # CommandSpec → CommandIR (formal IR)
src/init_deep/targets/registry.py     # Plugin registry (10 targets)
src/init_deep/targets/*.py            # Target plugins (plan → render)
    |
    v
src/init_deep/build.py                # build_v2(): renders all artifacts
src/init_deep/planner.py              # --dry-run, --diff, --json
src/init_deep/linter.py               # Semantic source validation
src/init_deep/doctor.py               # Workspace health checks
src/init_deep/cli.py                  # Unified CLI (build/check/lint/doctor/watch)
```

### Legacy layer (still functional)

```
source/init-deep/canonical.md          # Original single-file source
tools/init_deep/source.py             # CanonicalSource parser
tools/init_deep/renderers.py          # render_*() functions (8 platforms)
tools/init_deep/paths.py              # Centralized managed artifact paths
scripts/build_init_deep.py            # Legacy build script
scripts/check_init_deep.py            # Legacy check script
```

### Generated outputs

```
skills/init-deep/SKILL.md             # Claude Code skill
adapters/cursor.mdc                   # Cursor rule (trigger)
adapters/cursor/commands/init-deep.md  # Cursor full command
adapters/copilot.md                   # Copilot instructions (short)
adapters/copilot/prompts/*.prompt.md   # Copilot prompt (budget-truncated)
adapters/gemini/commands/*.toml        # Gemini CLI command
adapters/windsurf/init-deep.md         # Windsurf rules
adapters/cline/init-deep.md           # Cline rules
adapters/continue/                     # Continue prompts + rules
adapters/roo/                          # Roo instructions + skills
.claude-plugin/                        # Claude Code plugin metadata
```

### Key Files

| File | Role |
|------|------|
| `source/commands/init-deep/spec.toml` | Typed manifest: flags, metadata, intent |
| `source/commands/init-deep/body.md` | Markdown instructions (body content) |
| `source/init-deep/canonical.md` | Legacy single-file source (compat loader) |
| `src/init_deep/ir.py` | `CommandIR`, `SectionIR`, `ArtifactIR` frozen dataclasses |
| `src/init_deep/targets/registry.py` | Target plugin registry (10 built-in targets) |
| `src/init_deep/targets/base.py` | `TargetPlugin` protocol + `TargetCapabilities` |
| `tools/init_deep/paths.py` | Centralized managed artifact paths |
| `scripts/build_init_deep.py` | Legacy build (delegates to new pipeline) |
| `scripts/check_init_deep.py` | Byte-for-byte sync validation |
| `.claude-plugin/plugin.json` | Plugin manifest for Claude Code marketplace |
| `.github/workflows/validate.yml` | CI: check, build, diff, test, lint, validate configs |

## Conventions

- **Dual source format**: new commands use `spec.toml` + `body.md`; legacy `canonical.md` supported via compatibility loader
- **Target plugin architecture**: each platform is a `TargetPlugin` class in `src/init_deep/targets/` with `plan()`, `render()`, `validate()` methods
- **Generated artifacts checked in**: CI runs build then `git diff --exit-code` to enforce sync
- **No external dependencies**: pure Python stdlib (dataclasses, pathlib, re, textwrap, tomllib, unittest)
- **Frozen dataclasses**: `CommandSpec`, `CommandIR`, `SectionIR`, `ArtifactIR` are all immutable
- **Tests are integration-style**: read actual files from disk, no mocks, no fixtures (273 tests)
- **Derived files marked generated**: `.gitattributes` uses `linguist-generated=true` so GitHub collapses diffs
- **Contributing**: edit source (`spec.toml`/`body.md`), rebuild artifacts, include both in the same PR

## Known Pitfalls

- `textwrap.dedent` fails with f-string interpolation when the body lacks common indentation — use plain string concatenation in renderers instead
- Cursor `.mdc` rule uses `alwaysApply: false` — the full workflow lives in `commands/`, the rule just triggers it
- Copilot prompt is budget-truncated to 8KB — full workflow is in other adapters
- Gemini adapter is TOML (not Markdown) — validate with `tomllib` after changes
- `--skip-*` flags are CLI-only (generated from target names) — they don't belong in `spec.toml`
- Codex target generates no artifacts (reads `AGENTS.md` natively) — it exists for `--only codex` selection
- `managed_paths()` in `tools/init_deep/paths.py` uses glob patterns — update when adding new adapters
