# Contributing to init-deep

Thanks for contributing. This repository treats `source/init-deep/canonical.md`
as the source of truth. The files in `skills/` and `adapters/` are generated
artifacts and should change only as part of a rebuild from that canonical
source.

## Development workflow

1. Open an issue for larger bugs, feature requests, or behavior changes before
   starting work.
2. Edit `source/init-deep/canonical.md` for any change that affects generated
   assistant prompts or adapter output.
3. Rebuild generated artifacts in the same change whenever the canonical source
   changes.
4. Keep pull requests focused and explain user-visible behavior changes,
   validation changes, or documentation changes in the PR description.

## Local validation

Run the same checks used in CI before you open a pull request:

```bash
python3 scripts/check_init_deep.py
python3 scripts/build_init_deep.py
git diff --exit-code
python3 -m unittest discover -s tests -v
npx -y markdownlint-cli2 "README.md" "skills/**/*.md" "adapters/**/*.md" "adapters/**/*.mdc"
jq . .claude-plugin/plugin.json > /dev/null
jq . .claude-plugin/marketplace.json > /dev/null
```

## Pull requests

- Include regenerated files when `source/init-deep/canonical.md` changes.
- Update tests and README/docs in the same PR when behavior or flags change.
- Keep secrets, tokens, and personal workspace artifacts out of commits.

## Security

Please follow [SECURITY.md](SECURITY.md) for vulnerability reports. Do not post
sensitive details in a public issue or pull request.
