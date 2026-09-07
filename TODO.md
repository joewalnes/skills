# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

## Done

- [x] **P2** (feature) delegate-image: choose the output type; Astra for SVG — Joe asked, 2026-09-07 — 2026-09-07
  Resolved: output-type decision first; SVG panel (svg-panel.py: Astra + GLM 5.3 + Claude's own entry, XML-validated, rendered with rsvg-convert for the judges, animation only when asked); raster panel unchanged; Astra never used for raster.

- [x] **P1** (feature) go-team: apply the 48h fleet retro fixes — Joe asked, 2026-09-07 — 2026-09-07
  Resolved: heartbeat installed+verified by start, bypass instruction first, one preflight question + 10m timeout, foreman agent without AskUserQuestion, Done: lines, computed lane line, honest provenance, compass as script output; plus a computed heartbeat line replacing silence, push notifications, /fleets.

- [x] **P1** (feature) go-team: detect thrashing and step back without babysitting — Joe asked, 2026-09-07 — 2026-09-07
  Resolved: research-first brief for any artefact class the project hasn't built; stall alarm from lease age (6h, no landing) turns the seat's next message into a step-back brief; reader test in the gate for user-facing text.

- [x] **P2** (feature) New skill: high-quality documentation writing — Joe asked, 2026-09-07 — 2026-09-07
  Resolved: /docs (Diátaxis, audience-first plan, writing standard adapted from websocketd's STYLE.md, reader test, drift checks); scorecard Documentation dimension and Agent 4 updated.

- [x] **P2** (feature) New skill: /retro — evidence-driven process retrospective — 2026-09-07 — 2026-09-07
  Resolved: /retro with retro.py — timeline gaps, channels used vs defined, human redirects, fleet artefacts. Tested on websocketd.

- [x] **P2** (feature) Commit hygiene: frequent commits, consolidation before push — Joe asked, 2026-09-07 — 2026-09-07
  Resolved: /consolidate (contiguous-theme rebuild, tree-verified, backup tag), wired into go-team's gate, CLAUDE.md, project-setup, README. Dogfooded on this repo.

- [x] **P3** (chore) Split tool-web and project-setup into router + references — 2026-09-07 — 2026-09-07
  Resolved: tool-web 618→75 root lines (5 references); project-setup 366→78 (one-line pitch table + references/suggestions.md).
- [x] **P3** (chore) Standardize frontmatter fields across skills — 2026-03-31
  Resolved: Added `argument-hint` to all skills that accept arguments (bug-bash, project-setup, readme, scorecard, tool-web). Removed redundant `user_invocable: true` from tool-web. Documented frontmatter convention in CLAUDE.md: `name` and `description` required, `argument-hint` when args accepted, `allowed-tools` optional and enforced.


- [x] **P2** (bug) plugin.json has wrong repository URL — 2026-03-31
  Resolved: Changed `"repository"` from `joe/skills` to `joewalnes/skills` in `.claude-plugin/plugin.json`

- [x] **P2** (bug) Broken placeholder link in tool-web skill — 2026-03-31
  Resolved: Removed the "Onesies Integration" section entirely — it was project-specific boilerplate with a placeholder URL, not appropriate for a shared skill

- [x] **P3** (chore) Add .gitignore — 2026-03-31
  Resolved: Added `.gitignore` with standard exclusions (OS files, editor swap files, env files, logs)

- [x] **P1** (chore) Deduplicate /bug and /todo skills — 2026-03-31
  Resolved: Replaced 118-line copy-paste in `bug/SKILL.md` with thin wrapper delegating to `/todo`

- [x] **P1** (docs) README missing 6 of 8 skills — 2026-03-31
  Resolved: Added all 8 skills to README table in alphabetical order
