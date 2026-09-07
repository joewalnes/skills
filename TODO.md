# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

- [ ] **P1** (feature) go-team: apply the 48h fleet retro fixes — Joe asked, 2026-09-07
  Loop installed and verified by `start` (fleets were 90–99% idle: no heartbeat ever existed);
  bypass-mode instruction first (workers inherit the session's permission gate); one preflight
  `AskUserQuestion` with recommended defaults + `askUserQuestionTimeout: 10m`; foreman as a
  custom agent without AskUserQuestion; honest landing provenance + computed lane line;
  compass line as script output; `Done:` lines on ASKS entries; heartbeat re-reads SKILL.md.

- [ ] **P1** (feature) go-team: detect thrashing and step back without babysitting — Joe asked, 2026-09-07
  Retro the websocketd docs session: it generated junk revision after revision until Joe told it
  to go research alternatives (then found Diataxis). What signal says "stop and research" —
  N revisions of the same artifact with nothing landed? a check-in with no product movement?
  Make the trigger mechanical so the fleet does it unprompted.

- [ ] **P2** (feature) New skill: high-quality documentation writing — Joe asked, 2026-09-07
  Born from the websocketd docs mess. Diataxis IA (tutorial / how-to / reference / explanation),
  a writing standard, single-sourcing generated reference, drift checks that fail. Then update
  scorecard's Documentation dimension to grade against it.

- [ ] **P2** (feature) New skill: /retro — evidence-driven process retrospective — 2026-09-07
  Script the analysis done by hand on 2026-09-07: transcript timeline + idle gaps and what
  preceded each, tool-use channels used vs defined, fleet artefacts vs ASKS status, the human's
  own interjections. Output: rule + mechanism + scope proposals via `/request skills`.

- [ ] **P2** (feature) delegate-image: choose the output type; Astra for SVG — Joe asked, 2026-09-07
  Judge output type per request: logos, icons and diagrams are usually better as SVG (text — authored
  directly, reviewable, animatable via SVG/CSS); photos and scenes stay raster. When SVG is the right
  type, the panel is text models: GPT-6 Astra (ZDR on OpenRouter, confirmed by Joe) alongside the
  existing models. When raster, Astra is not used. Same two-judge review either way; judges see
  the SVG rendered, not the source.

- [ ] **P2** (feature) Commit hygiene: frequent commits, consolidation before push — Joe asked, 2026-09-07
  The fleets' logs are huge and thrashy. Keep committing often on branches, but before a push (and in
  go-team's gate, before a worker branch merges) rebuild the range into clean atomic commits by theme
  — the soft-reset + per-theme checkout technique, verified tree-identical. Likely a `/consolidate`
  skill with a script, wired into the gate and the dev loop.

- [ ] **P3** (chore) Split tool-web and project-setup into router + references — 2026-09-07
  The two monoliths left from the Provencher audit (618 and 370 lines). Read tool-web first.

## Done

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
