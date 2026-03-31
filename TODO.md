# Todo

<!-- Format: [status] P<priority> (category) Title -->
<!-- Status: [ ] open, [~] in progress, [x] done, [-] won't fix -->
<!-- Priority: P0 critical, P1 high, P2 medium, P3 low -->
<!-- Category: bug, feature, chore, docs -->

## Open

- [x] **P2** (bug) plugin.json has wrong repository URL — 2026-03-31
  Resolved: Changed `"repository"` from `joe/skills` to `joewalnes/skills` in `.claude-plugin/plugin.json`

- [ ] **P2** (bug) Broken placeholder link in tool-web skill
  `skills/tool-web/SKILL.md:465` has `https://github.com/...` — either fill in the real URL or remove the Onesies Integration section

- [ ] **P3** (chore) Add .gitignore
  Repo has no .gitignore — should exclude `.DS_Store`, `.env`, `*.log`, etc.

- [ ] **P3** (chore) Standardize frontmatter fields across skills
  `argument-hint`, `allowed-tools`, `user_invocable` used inconsistently — define which are required vs optional

## Done

- [x] **P1** (chore) Deduplicate /bug and /todo skills — 2026-03-31
  Resolved: Replaced 118-line copy-paste in `bug/SKILL.md` with thin wrapper delegating to `/todo`

- [x] **P1** (docs) README missing 6 of 8 skills — 2026-03-31
  Resolved: Added all 8 skills to README table in alphabetical order
