# init-deep — AI Documentation Generator for Coding Assistants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/mzored/init-deep/actions/workflows/validate.yml/badge.svg)](https://github.com/mzored/init-deep/actions/workflows/validate.yml)
![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)

init-deep is a codebase documentation tool that scans your project and generates platform-native context files so every AI coding assistant understands it. It runs as a slash command inside your AI assistant and writes the right documentation for each platform automatically — no manual maintenance required.

## Why init-deep

AI coding assistants work best when they have accurate, up-to-date context about your project — files like `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/`. Creating and keeping this AI assistant context synchronized across multiple platforms manually is tedious and error-prone. init-deep automates code documentation: it analyzes your project once and produces correctly formatted files for each platform from a single canonical source.

## Supported Platforms

- **Claude Code** — generates `CLAUDE.md` (project context) and scoped `.claude/rules/*.md` files
- **OpenAI Codex CLI** — generates `AGENTS.md` (the canonical source; read natively by Codex)
- **Cursor** — generates `.cursor/rules/*.mdc` (scoped module rules) and `.cursor/commands/init-deep.md`
- **Google Gemini CLI** — generates `GEMINI.md` (project context derived from `AGENTS.md`)
- **GitHub Copilot** — generates `.github/copilot-instructions.md` and `.github/prompts/init-deep.prompt.md`
- **Windsurf** — generates `.windsurfrules`
- **Cline** — generates `.clinerules`

## Quick Start

Install init-deep into Claude Code from the plugin marketplace:

```bash
claude plugin marketplace add mzored/init-deep
claude plugin install init-deep
```

Then, inside a Claude Code session in your project directory, run:

```text
/init-deep
```

init-deep will analyze your codebase and generate or update all documentation files.

## Installation

### Claude Code

```bash
claude plugin marketplace add mzored/init-deep
claude plugin install init-deep
```

Or from an interactive Claude Code session:

```text
/plugin marketplace add mzored/init-deep
/plugin install init-deep
```

### OpenAI Codex CLI

```bash
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
mkdir -p ~/.codex/skills/init-deep
cp /tmp/init-deep/skills/init-deep/SKILL.md ~/.codex/skills/init-deep/SKILL.md
rm -rf /tmp/init-deep
```

### Cursor

```bash
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
mkdir -p .cursor/commands .cursor/rules
cp /tmp/init-deep/adapters/cursor/commands/init-deep.md .cursor/commands/init-deep.md
cp /tmp/init-deep/adapters/cursor.mdc .cursor/rules/init-deep.mdc
rm -rf /tmp/init-deep
```

### Google Gemini CLI

```bash
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
mkdir -p .gemini/commands
cp /tmp/init-deep/adapters/gemini/commands/init-deep.toml .gemini/commands/init-deep.toml
rm -rf /tmp/init-deep
```

### GitHub Copilot

```bash
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
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
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
cp /tmp/init-deep/adapters/windsurf/init-deep.md .windsurfrules
rm -rf /tmp/init-deep
```

### Cline

```bash
git clone https://github.com/mzored/init-deep.git /tmp/init-deep
cp /tmp/init-deep/adapters/cline/init-deep.md .clinerules
rm -rf /tmp/init-deep
```

## Usage

init-deep runs as a slash command inside your AI assistant. All flags work across platforms that support them:

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

## How It Works

init-deep generates AI-ready project documentation through a four-step pipeline. The output is a set of platform-native files — `AGENTS.md` for Codex, `CLAUDE.md` for Claude Code, and adapter files for Cursor, Copilot, Gemini, Windsurf, and Cline:

1. **Discovery** — concurrent analysis of project structure, conventions, entry points, anti-patterns, build/CI configuration, and test patterns
2. **Scoring** — each directory is scored to determine whether it warrants its own scoped documentation file
3. **Generation** — `AGENTS.md` is produced as the canonical source; all other platform files are derived from it
4. **Review** — cross-file sync verification, deduplication, and size trimming to keep each file within platform limits

## Generated Files

| File | Platform | Purpose |
|------|----------|---------|
| `AGENTS.md` | OpenAI Codex | Universal agent instructions (canonical source) |
| `CLAUDE.md` | Claude Code | Claude context, derived from AGENTS.md |
| `GEMINI.md` | Google Gemini CLI | Gemini context, derived from AGENTS.md |
| `.github/copilot-instructions.md` | GitHub Copilot | Copilot-specific context |
| `.cursor/rules/*.mdc` | Cursor | Scoped module docs |
| `.windsurfrules` | Windsurf | Windsurf context |
| `.clinerules` | Cline | Cline context |
| `.claude/rules/*.md` | Claude Code | Scoped module docs |

## Development

The source of truth for all generated artifacts lives in `source/commands/init-deep/` (`spec.toml` + `body.md`). The legacy single-file format `source/init-deep/canonical.md` is also supported. After editing source files, rebuild and validate:

```bash
python3 -m src.init_deep.cli build
python3 -m src.init_deep.cli check
git diff --exit-code
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the generated-artifact workflow and validation commands, and [SECURITY.md](.github/SECURITY.md) for private vulnerability reports.

## License

[MIT](LICENSE)
