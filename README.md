# Skills

A collection of custom Claude Code skills.

## Installation

### Option 1: Global install (recommended)

Symlinks skills into `~/.claude/skills/` so they're available as `/skill-name` in every project, on every machine.

```bash
git clone https://github.com/joewalnes/skills.git
cd skills
make install
```

Skills are symlinked, not copied — edits made by Claude in any project write back to this repo, making it easy to commit and push upstream.

To remove:

```bash
make uninstall
```

### Option 2: Plugin install (namespaced)

Install as a Claude Code plugin. Skills are available as `/skills:skill-name`.

```
/plugin install https://github.com/joewalnes/skills
```

### Other commands

```bash
make list       # Show available skills and install status
```

## Skills

| Skill | Description |
|-------|-------------|
| `bug` | Add a new bug to the project's tracker (alias for `/todo`) |
| `bug-bash` | Autonomously work through a project's bug list, fixing bugs in priority order |
| `delegate-bulk` | Delegate high-volume, low-intelligence grunt work to a cheap model |
| `delegate-image` | Generate an image via a panel of top image models, critiqued by independent AI judges |
| `delegate-private` | Delegate work on private data to a local on-device model that never leaves the machine |
| `delegate-review` | Get an independent second-opinion code review from a different model lineage |
| `delegate-security-audit` | Delegate deep security analysis and fixes to GLM |
| `go-team` | Run a crew of parallel agents on a project — dispatch, verify behaviourally, gate, merge |
| `hello-world` | A simple test greeting skill |
| `project-setup` | Walk through project setup improvements for AI-assisted development |
| `readme` | Generate or update project README documentation |
| `release-setup` | Set up automated cross-platform binary releases for a Go project |
| `scorecard` | Comprehensive codebase quality audit with letter grades |
| `sitrep` | Quick situation report — recap progress, uncommitted work, gaps, and next steps |
| `todo` | Add a new bug or todo to the project's tracker |
| `tool-web` | Build a lightweight single-file web application with no external dependencies |

## Development

Test locally:

```bash
claude --plugin-dir .
```

## License

MIT
