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

## The dev loop

Most of these skills are designed to run as one loop, not as isolated commands. Set a project up once, capture work as it arrives, hand it to agents, check in, audit, and feed the audit back into the queue.

```
                 /project-setup   (once per project)
                        │
                        ▼
   ideas, bugs ──►   /todo   ──►  TODO.md  ◄──────────────────┐
   your own asks ──────────────►  ASKS.md                     │
                        │                                     │
                        ▼                                     │
              /bug-bash   one agent, while you watch          │
              /go-team    a crew, unattended — overnight      │
                        │                                     │
                        ▼                                     │
                    /sitrep   what landed · what's running    │
                              · what's blocked on YOU         │
                        │                                     │
                        ▼                                     │
                  /scorecard  ── findings ────────────────────┘
```

**1. Set up once — `/project-setup`.** Walks through the scaffolding the rest of the loop depends on: a tracker (`TODO.md`), an engineering diary, `CLAUDE.md` rules, and — the one that decides whether an overnight run survives — a permissions allowlist so agents don't stall on a prompt at 2am. Run it again later with `status` to see what's missing.

**2. Capture work as it comes — `/todo`.** Braindump bugs and ideas into the tracker as you notice them, without breaking flow. Your *own* requests go in `ASKS.md`, a separate lane that agents rank above everything they found for themselves — otherwise a feature you designed sits unbuilt for twelve hours while agents fix bugs in the thing it was meant to replace.

**3. Do the work.** Two modes:
- **`/bug-bash`** — one agent works the tracker in priority order while you're around.
- **`/go-team`** — a crew of agents runs unattended, pulling from `ASKS.md`, then `TODO.md`, then `/scorecard` findings. Built on one premise: agents systematically overstate what they've done, so nothing merges on a report — every claim is reproduced in an isolated worktree first. It degrades rather than stalls: a missing recipe or an unanswerable question narrows the scope, it never stops the fleet. Run it on `/loop` and go to bed.

**4. Check in — `/sitrep`.** When you come back: what landed, what's still running, and — first, above everything — anything waiting on a decision or permission only you can give. A blocked agent is the only line in a status report still costing you something while you read it.

**5. Audit, and feed it back — `/scorecard`.** Periodic letter-graded health check across 13 code dimensions plus a second table for *agent-readiness*: could an agent work here for eight hours without a human? Its Security grade cross-checks against `/delegate-security-audit` for a second model's opinion. Findings go back into the tracker, where `/go-team` picks them up.

**5b. Watch for slop — `/slop`.** Cheap code has a failure mode that looks fine commit by commit: every change adds a guard, a fallback, a special case, and nothing is ever folded back. `/slop` measures whether a repo is accreting — splitting history into a hand-written era and an AI era when it can — and, run on a branch, asks the one question that separates a chosen change from an unchosen one: *could the author say why?* It grades on articulability and surface area, explicitly not on diff size; a big refactor with one thesis passes, a small fix with none doesn't.

| Skill | Role in the loop |
|-------|------------------|
| `project-setup` | Establish the scaffolding once (tracker, diary, rules, unattended permissions) |
| `todo` / `bug` | Capture work into the tracker without breaking flow |
| `bug-bash` | Work the tracker with one agent, attended |
| `go-team` | Work the tracker with a crew, unattended; verify before merging |
| `sitrep` | Resume: what landed, what's running, what's blocked on you |
| `scorecard` | Periodic audit; findings feed back into the tracker |
| `slop` | Audit for *unchosen* code — accretion trends on a repo, or a pre-merge check on a branch |

## On-demand skills

For a specific task, outside the loop.

**Delegating to other models.** Claude can't generate images, and sometimes a second opinion from a different model lineage, a local-only model for private data, or a cheap model for grunt work is the right tool. These route through `pi` and OpenRouter, honouring a zero-data-retention-only policy.

| Skill | Description |
|-------|-------------|
| `delegate-bulk` | High-volume, low-intelligence grunt work on a near-free model |
| `delegate-image` | Generate an image via a panel of top image models, with two independent AI judges picking their favourites |
| `delegate-private` | Work on private data with a local on-device model that never leaves the machine |
| `delegate-review` | Independent second-opinion code review from a different model lineage |
| `delegate-security-audit` | Deep security analysis and fixes via GLM |

**Building and shipping.**

| Skill | Description |
|-------|-------------|
| `readme` | Generate or update project README documentation |
| `release-setup` | Set up automated cross-platform binary releases for a Go project |
| `tool-web` | Build a lightweight single-file web application with no external dependencies |
| `hello-world` | A simple test greeting skill |

## Development

Test locally:

```bash
claude --plugin-dir .
```

## License

MIT
