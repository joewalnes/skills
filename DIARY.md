# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-05-17 — `tool-web` CSS replaced with House Style (3-section token system)

Swapped the ad-hoc CSS guidance (minimal reset, free-form typography catalog, hex-coded `#111`/`#555`/`#999` visual hierarchy) for a **House Style** organised as three independent sections: Reset (required), Typography (optional), Color (optional). All colors are now OKLCH tokens (`--bg`, `--bg-muted`, `--text-heading`, `--text-body`, `--text-muted`, `--border`, `--accent`, `--link`, …) driven by a single `--hue` knob. Light/dark auto-follow OS with `data-theme="light|dark"` override.

**Decisions and conflicts resolved:**

- **Heading-weight direction flipped** from lighter-as-larger (h1: 300 → h3: 500) to heavier-as-larger (h1: 900 → h4: 600). The old approach was a deliberate aesthetic ("consistent perceived stroke width") that works well for refined display type; the new approach is more conventional, has more punch with slab/serif headings, and the source spec explicitly marks it as non-configurable. House Style wins over per-tool taste — that's the whole point of a house style.
- **Hardcoded colors deleted.** `#111 / #555 / #999` is replaced by the `--text-*` tiers. The `Visual Hierarchy` subsection was replaced by a token-rules subsection ("Styling new elements").
- **Font-stack catalog shrunk** from ~14 named stacks to four (`--sans-serif`, `--serif`, `--code`, `--slab`). Link to modernfontstacks.com retained for users who want more variety.
- **`-webkit-font-smoothing: antialiased` dropped** — modern best practice is not to force it; it makes text look thinner than designed on macOS.
- **Universal `padding: 0` reset dropped** — was too aggressive (broke `<button>`, list defaults). Only `margin: 0` resets now.
- **`min-height: 100dvh` kept** on body (better than `100vh` for mobile chrome) even though the source spec used `100vh`.
- **`.template { display: none !important }` merged into Section 1** — it's load-bearing for the stamp pattern.

**Known issues flagged in the doc:**

- Heading text hue is fixed at 280 regardless of `--hue` (by design — cool text + warm bg + hue-driven accent — but worth telling the user).
- Hover/chart guidance uses `oklch(from var(--accent) …)` relative-color syntax, which needs Chrome 119+ / Safari 16.4+ / Firefox 128+. Inside the modern-browsers target, but tighter than plain `oklch()`.

**Follow-ups landed same day:**

- **Dark palette de-duplicated** using `light-dark()` plus `color-scheme: light dark` at `:root`. Each token now reads `light-dark(L, D)` in one place; `[data-theme="light"|"dark"]` flips `color-scheme` and every token follows. Lifts the browser-support floor for Section 3 to Chrome 123 / Safari 17.5 / Firefox 120, but those are all from late 2023 / early 2024 — fine for the target.
- **`prefers-reduced-motion` guard** added to Section 3, disabling the 200ms body color transition when the user has the OS reduce-motion preference set. The earlier "flash on first paint" concern I noted was overstated — CSS transitions don't run on initial computed value, only on subsequent changes. The guard is purely an a11y courtesy for theme toggles and OS-preference changes, not a flash mitigation.
- **Worked Example section added** between JavaScript and External Dependencies — a complete copy-pasteable `notes.html` that exercises all three House Style sections, the stamp pattern, and event delegation. Concrete demonstration of "page-specific CSS never names a color or px font size."

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
