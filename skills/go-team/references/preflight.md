# go-team — Preflight

Part of the `/go-team` skill; read on `start`, or the first cycle on a project. The loop itself is in `SKILL.md`.

## Phase 0 — Preflight

**Everything in this phase belongs to the minutes while the human is still awake.** The fleet exists for the hours after they walk away, and a question asked in those hours costs the entire remainder of the run — not the two minutes it takes to answer. Front-load every question here, or proceed without asking at all.

The governing asymmetry: **it is always worth interrupting to prevent an eight-hour stall, and never worth interrupting to avoid a two-minute one.**

### 0a. Unattended readiness — check this before anything else

Confirm the fleet can actually act without a prompt. This is the most common way an overnight run dies — not a crash, not a bad merge, but five agents parked behind a permission dialog at minute three while the human sleeps.

Check the project's `.claude/settings.json` (and `~/.claude/settings.json`):

- **`permissions.defaultMode`** — `acceptEdits` at minimum. The plain default prompts on every write, which is every agent, constantly.
- **`permissions.allow`** — must cover the commands the verification recipe actually invokes. Read the recipe, list its binaries (`cargo build`, `npm test`, `git commit`, whatever it is), and confirm each appears. A recipe the fleet cannot run unprompted is not a recipe.
- **Blocking hooks** — a `PreToolUse` hook that exits non-zero halts the call. That is correct for a guard and fatal for anything interactive.

**If something is missing and the human is here, say so now and offer the fix** — this is a one-line settings edit, not a project. **If they are already gone** (an unattended `/loop` fired this), do not stall: run anyway and report the gap in the first digest.

### 0b. The project's configuration

**Read the project's `CLAUDE.md`.** It carries the per-project configuration this skill depends on. Look for a `## Agent operations` section containing:

- **Verification recipe** — how to drive the real thing (not just run tests)
- **Autonomy policy** — merge-and-push, or merge-locally-only
- **Shared singletons** — machine-wide resources agents must not share
- **Do-not-touch** — settled decisions, parked proposals, accepted limits
- **Global-blast-radius files** — the short list of places where any change has global effect (default configs, prompts, ranking/fusion loops, abstention gates, the production asset), each guarded by a test that fails on content change without an explicit marker. Twice an agent decided something it was explicitly told to escalate; the escalation instruction was a wish. Constrain behaviour, not text — and keep the list short or it becomes noise.
- **Requests lane** — path to the file holding the human's own asks (default `ASKS.md`)
- **Setup version** — the `project-setup` version this project has adopted

**If that section is missing and the human is present, run `/project-setup` first.** Do not improvise the scaffolding. Without a verification recipe the central rule of this skill — verify behaviourally before merging — has nothing to stand on, and you will fall back to trusting reports, which is the failure this skill exists to prevent.

**If that section is missing and the human is gone, do not stop.** Run a reduced fleet on work whose deliverable is a *report* rather than a merge: adversarial hunts, audits, `/scorecard` runs, findings written to the tracker. Merge nothing — without a recipe you cannot honour the verification rule, and merging on reports is the exact failure this skill prevents. Say plainly in the first digest that the run was scope-limited and why. Eight hours of findings beats eight hours of a stopped fleet holding a question.

**If the setup version is behind the current `project-setup`,** offer the delta if the human is present; note it in the digest and carry on if not.

**On the first run** (`/go-team start`), confirm with the human:
- agent count — **default 3 workers plus the foreman**, one per seat (see *Three seats*), and the cost implication
- autonomy: push to remote, or merge locally only

Record both in `CLAUDE.md` so you never ask twice. `start` is an attended command by design — if an unattended run hits an unconfigured project, take the defaults (3 workers, merge-locally-only: the safer half of each choice) and report that you did rather than waiting to be told.

**Width is a measured decision, not a habit.** Contention, merge fan-in, tracker-numbering collisions and duplicate dispatch all scale with concurrency; each extra agent stretches every other agent's builds and multiplies reconciliation. In the 48-hour run that shaped this section, roughly a third of all commits were the fleet fixing, reconciling or re-doing its own work, and the throughput gain above 2–3 agents was never established. Widen only when the foreman can name the number that says the bottleneck is worker count, and hold "at N" as a bound backed by that number. Three is the floor at which every seat has an occupant; widening adds product seats, never a fourth kind of seat.

---

