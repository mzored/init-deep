<!-- Derived from AGENTS.md by /init-deep. Keep in sync. -->
# init-deep

Multi-platform AI documentation compiler. Python 3.11, no external deps.

## Commands

```bash
python3 scripts/build_init_deep.py       # Regenerate adapters
python3 scripts/check_init_deep.py       # Validate sync
python3 -m src.init_deep.cli check       # Validate registry-generated adapters
python3 -m src.init_deep.cli lint        # Validate source schema
python3 -m src.init_deep.cli doctor      # Check workspace health

python3 -m unittest discover -s tests -v # Run tests
```

## Architecture

Two-layer design: a typed compiler pipeline and a legacy compatibility layer.

**New pipeline:** `source/commands/init-deep/spec.toml` + `body.md` are parsed into `CommandSpec`, lowered to `CommandIR`, and rendered by 9 built-in target plugins in `src/init_deep/targets/`.

**Legacy:** `source/init-deep/canonical.md` is the original single-file source. `tools/init_deep/renderers.py` generates platform-specific output. Legacy scripts delegate to the new pipeline.

## Conventions

- Edit `spec.toml` + `body.md`; keep `source/init-deep/canonical.md` byte-identical for legacy compatibility
- Never hand-edit generated `skills/` or `adapters/`; rebuild them
- CI enforces sync: build then `git diff --exit-code`
- Pure stdlib Python, no external dependencies
- Each platform is a `TargetPlugin` class with `plan()`, `render()`, `validate()` methods
- Tests read actual files, no mocks (273+ tests)

## Pitfalls

- Gemini adapter is TOML, not Markdown
- Copilot instructions and prompts are budget-sensitive; do not assume the prompt contains the full workflow
- `managed_paths()` glob list must be updated when adding adapters
- `--skip-*` flags are CLI-only, not in `spec.toml`
