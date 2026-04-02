# init-deep

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Deep codebase analysis and multi-agent documentation generator. The checked-in artifacts in `skills/` and `adapters/` are generated from `source/init-deep/canonical.md`; edit the canonical source and rebuild instead of hand-editing distribution files.

## What it does

`/init-deep` scans your codebase — structure, conventions, entry points, anti-patterns, build/CI — and generates platform-specific documentation so every AI coding assistant understands your project.

| Generated file | Read by | Purpose |
|----------------|---------|---------|
| `AGENTS.md` | OpenAI Codex | Universal agent instructions (canonical source) |
| `CLAUDE.md` | Claude Code | Claude context, derived from AGENTS.md |
| `GEMINI.md` | Google Gemini CLI | Gemini context, derived from AGENTS.md |
| `.github/copilot-instructions.md` | GitHub Copilot | Copilot-specific context |
| `.cursor/rules/*.mdc` | Cursor | Scoped module docs |
| `.windsurfrules` | Windsurf | Windsurf context |
| `.clinerules` | Cline | Cline context |
| `.claude/rules/*.md` | Claude Code | Scoped module docs |

## Installation

### Claude Code

```bash
claude plugin marketplace add MZored/init-deep
claude plugin install init-deep
```

### OpenAI Codex CLI

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
mkdir -p ~/.codex/skills/init-deep
cp /tmp/init-deep/skills/init-deep/SKILL.md ~/.codex/skills/init-deep/SKILL.md
rm -rf /tmp/init-deep
```

### Cursor

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
mkdir -p .cursor/commands .cursor/rules
cp /tmp/init-deep/adapters/cursor/commands/init-deep.md .cursor/commands/init-deep.md
cp /tmp/init-deep/adapters/cursor.mdc .cursor/rules/init-deep.mdc
rm -rf /tmp/init-deep
```

### Google Gemini CLI

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
mkdir -p .gemini/commands
cp /tmp/init-deep/adapters/gemini/commands/init-deep.toml .gemini/commands/init-deep.toml
rm -rf /tmp/init-deep
```

### GitHub Copilot

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
mkdir -p .github/prompts
cp /tmp/init-deep/adapters/copilot/prompts/init-deep.prompt.md .github/prompts/init-deep.prompt.md
cp /tmp/init-deep/adapters/copilot.md .github/copilot-instructions.md
rm -rf /tmp/init-deep
```

Copilot prompt files require prompt-file support. In VS Code, enable
`chat.promptFiles` before expecting `.github/prompts/init-deep.prompt.md`
to appear in the prompt picker.

### Windsurf

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
cp /tmp/init-deep/adapters/windsurf/init-deep.md .windsurfrules
rm -rf /tmp/init-deep
```

### Cline

```bash
git clone https://github.com/MZored/init-deep.git /tmp/init-deep
cp /tmp/init-deep/adapters/cline/init-deep.md .clinerules
rm -rf /tmp/init-deep
```

## Usage

### Shared flags

```bash
/init-deep                      # Update existing docs + create new where needed
/init-deep --create-new         # Regenerate all docs from scratch
/init-deep --max-depth=2        # Limit directory analysis depth (default: 3)
/init-deep --only=claude,codex  # Generate only specific formats
/init-deep --skip-cursor        # Skip Cursor format generation
/init-deep --skip-gemini        # Skip Gemini format generation
/init-deep --skip-copilot       # Skip Copilot format generation
/init-deep --skip-windsurf      # Skip Windsurf format generation
/init-deep --skip-cline         # Skip Cline format generation
/init-deep --dry-run            # Preview scores and planned writes
/init-deep --doctor             # Audit existing agent docs and install paths
/init-deep --sync-check         # Verify generated files are in sync with the canonical source
```

## How it works

1. **Discovery** — Concurrent analysis of project structure, conventions, entry points, anti-patterns, build/CI, and test patterns
2. **Scoring** — Each directory scored to determine if it needs its own scoped documentation
3. **Generation** — `AGENTS.md` generated as canonical source, all other files derived from it
4. **Review** — Cross-file sync verification, deduplication, size trimming

## Keeping docs in sync

`source/init-deep/canonical.md` is the canonical source of truth for this repository. After editing it, rebuild the generated artifacts and rerun validation so `skills/`, `adapters/`, and metadata stay synchronized.

## Contributing

Contributions welcome! Please open an issue or PR.

## License

[MIT](LICENSE)
