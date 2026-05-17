# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-05-17 — `el()` gains event-listener binding

Extended the `el()` helper in `tool-web` to bind functions passed under `on*` keys as event listeners via `addEventListener`, rather than coercing them into string attributes. Previously the skill explicitly called this out as a non-feature ("deliberately simple — no event binding"), and the recommended approach was to attach listeners on the returned element after creation.

**Why change it:** in practice, one-off elements created with `el()` (buttons, inputs in small forms) frequently need a single handler, and the extra `myBtn.onclick = ...` line breaks the otherwise nested, declarative shape of `el()` calls. Detecting `typeof v === 'function'` on `on*`-prefixed keys is a tiny amount of code and reads like inline HTML (`onclick`, `oninput`) while still using `addEventListener` underneath so listeners stack instead of overwrite.

**Why `on*` prefix instead of any function value:** keeps the convention visually distinct from attributes at the call site and avoids surprise if someone passes a function for an attribute that happens to share a name with an event. Listener options (`{ once: true }`, `{ passive: true }`) intentionally not supported through `el()` — bind on the returned element for that. Event delegation remains the preferred pattern for stamped/dynamic content; `on*` is for one-off elements.

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
