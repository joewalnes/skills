# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-09-01 — /delegate: external non-Claude agents

Joe was manually copy-pasting between Claude Code and other AI tools for jobs Claude models don't cover: image generation, deep security audits, work on private data that must stay on-device, second-opinion reviews from a different model lineage, and cheap bulk grunt work. Built `/delegate` so these run as briefed sub-agents from inside Claude Code.

Everything routes through tools already installed rather than new integrations: `pi` (the open-source coding agent, already configured with his OpenRouter key and local Ollama) does all text-model delegation via `pi -p`, and a small Python script calls OpenRouter's chat-completions image modality directly, fetching the key at runtime via `pi auth print-api-key` so no credentials live in the repo.

**Decisions:**
- One skill with an agent roster (image/sec/private/review/bulk) rather than five skills — the roster table is the extension point, and the briefing/reporting pattern is shared.
- Persistent `--session-id delegate-<agent>` per agent so follow-up delegations continue with memory, like real colleagues.
- The `private` agent's value is a *protocol*, not just a local model: Claude must never read the private material or its outputs — everything in Claude's context leaves the device. Paths in, file paths out, stdout kept non-sensitive.
- Joe's OpenRouter account rejects non-ZDR (zero data retention) endpoints by design; the skill treats those 404s as intentional and forbids suggesting the setting be loosened. Most `:free` models fail this, so `bulk` defaults to near-free `gemini-2.5-flash-lite` instead.
- Review default is Kimi K3, not GPT 5.6 Sol — Sol reserves 128k output tokens per request, which trips OpenRouter's daily-credit 402 on this account.

All five paths smoke-tested live (image gen produced a real PNG; GLM 5.3, qwen3.6 local offline, Kimi K3, and flash-lite each round-tripped).

---

## 2026-03-31 — Repo hygiene pass

Ran `/scorecard` on the repo — got **C+** overall. Main findings: massive DRY violation between `/bug` and `/todo` (95% identical), README only listed 2 of 8 skills, no `.gitignore`, and `plugin.json` had wrong GitHub URL.

**Changes made:**
- Deduplicated `/bug` into a thin 1-line wrapper that delegates to `/todo`. Chose the "thin wrapper" approach over a symlink because it preserves a separate name/description in frontmatter.
- Updated README with all 8 skills.
- Created `CLAUDE.md` with project conventions (first-time setup, adding-a-skill checklist).
- Created `/import-skill` as a project-local skill (`.claude/skills/`) — it discovers skills from `~/.claude/skills/` and sibling project directories, then walks through importing them. Kept it project-local since it's specific to this repo's structure.
- Created `/project-setup` skill for walking through AI-friendly project setup improvements.

**Decisions:**
- Skills that are aliases (like `/bug` → `/todo`) use a thin wrapper SKILL.md rather than symlinks, so they can have distinct names and descriptions.
- Project-specific skills live in `.claude/skills/`, shared/distributable skills live in `skills/`. The Makefile only installs `skills/`.
- Sibling project discovery in `/import-skill` assumes all git repos are checked out in the same parent directory — matches the user's workflow.

---

## 2026-03-31 — Initial commit

Bootstrapped shared skills repo with Makefile-based symlink installation (global or plugin mode). Started with 2 skills (hello-world, sitrep), then added 6 more (bug, bug-bash, readme, scorecard, todo, tool-web) in a second commit.

Key design choice: skills are symlinked, not copied. Edits in any project write back to this repo, making it easy to iterate on skills and push upstream.
