# Contributing to init-deep

Thanks for contributing. This repository generates platform-specific AI
documentation from structured source files. The files in `skills/` and
`adapters/` are generated artifacts and must change only as part of a rebuild.

## Source format

New commands use a two-file source format:

- `source/commands/<name>/spec.toml` — typed manifest (flags, metadata, intent)
- `source/commands/<name>/body.md` — markdown body (instructions)

Legacy commands also support `source/init-deep/canonical.md` via a compatibility
loader.

## Development workflow

1. Open an issue for larger bugs, feature requests, or behavior changes before
   starting work.
2. Edit source files (`spec.toml` + `body.md` or `canonical.md`) for any change
   that affects generated assistant prompts or adapter output.
3. Rebuild generated artifacts in the same change whenever source files change.
4. Keep pull requests focused and explain user-visible behavior changes,
   validation changes, or documentation changes in the PR description.

## Local validation

Run the same checks used in CI before you open a pull request:

```bash
# New CLI (preferred)
python3 -m src.init_deep.cli check       # Validate sync
python3 -m src.init_deep.cli build       # Regenerate adapters from source
python3 -m src.init_deep.cli lint        # Validate source schema and semantics
python3 -m src.init_deep.cli doctor      # Check workspace health

# Legacy scripts (still functional)
python3 scripts/check_init_deep.py
python3 scripts/build_init_deep.py

# Common checks
git diff --exit-code                     # Verify no uncommitted drift
python3 -m src.init_deep.cli check       # Validate registry-generated adapters
python3 -m unittest discover -s tests -v # Run all tests

# Markdown and config validation
npx -y markdownlint-cli2 "README.md" "skills/**/*.md" "adapters/**/*.md" "adapters/**/*.mdc"
jq . .claude-plugin/plugin.json > /dev/null
jq . .claude-plugin/marketplace.json > /dev/null
jq . .codex-plugin/plugin.json > /dev/null
jq . .agents/plugins/marketplace.json > /dev/null
```

## Pull requests

- Include regenerated files when source files change.
- Update tests and README/docs in the same PR when behavior or flags change.
- Keep secrets, tokens, and personal workspace artifacts out of commits.

## Security

Please follow [SECURITY.md](SECURITY.md) for vulnerability reports. Do not post
sensitive details in a public issue or pull request.
