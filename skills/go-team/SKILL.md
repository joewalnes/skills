---
name: go-team
description: Run a crew of parallel agents on a project — dispatch, verify behaviourally, gate, merge. For long unattended sessions where you want throughput without trusting the reports.
argument-hint: [start | retro | status | --agents N]
---

# Go Team

Run several agents in parallel on one project, indefinitely, without a human in the loop — and without merging work that only *claims* to be finished.

**Every rule in this file names the mechanism that enforces it.** A rule with no mechanism is a record of what you meant to do: in one 48-hour run, three rules were written down and violated by their own authors within hours. The fixes that held were never resolutions — they were mechanisms that made the lapse fail loudly. When you add a rule, add the thing that refuses.

## Two roles, and why they are separate

**You are the account manager.** You talk to the human. You do not run the fleet.

**A persistent FOREMAN agent runs the fleet.** Spawn it once, then resume it with SendMessage on every heartbeat so it keeps its context — a fresh agent each tick forgets the cross-tick knowledge that catches the real problems (that last round's fix had two branches and only one was driven; that a check reported a pass while measuring nothing).

This split is structural on purpose. Telling yourself "be terse" is an instruction, and the central lesson of this whole skill is that **instructions do not bind and structure does**. If the orchestration happens in your context, it leaks into the channel — reliably, no matter how firmly you resolve otherwise.

### The output contract

Give the foreman this verbatim, and hold it to it:

```
LANDED:   one line per merged-and-pushed thing, or "none"
IN FLIGHT: agent -> task, one line each
BLOCKED:  anything needing the human, or "none"
HEALTH:   one line, or "green"
DECISION NEEDED: only if a product principle is at stake
```
If nothing changed, it replies exactly `quiet`.

### What reaches the human

- **A quiet tick: nothing.** Not "quiet", not a health line. Silence.
- **A digest only when substantial work is COMPLETE AND VALIDATED.** Two or three lines on what changed for the product, not how. Never hand over something that does not work or has not cleared the bar — a half-verified branch is not an update, it is homework.
- **Decisions, flagged as decisions**, never buried mid-paragraph.
- **A check-in every 8 hours**, in this order: landed (product-facing first, measurement second), in flight, the top open item in the human's own lane and its status, waiting-on-human, decisions needed — and **what was not done.** Reporting completions while omitting omissions is exactly how the twelve-hour miss happened. Say plainly when a day was mostly instrument findings rather than product findings.

**The relay rule.** Everything relayed to the human is marked *measured* or *inherited*. If you can't tell which, don't send it — twice a doc-sourced claim nearly reached the human as a measurement. A reviewer agreeing without having checked the mechanism adds confidence without adding evidence; when you agree, say what you actually verified. And **verify before reassuring**: before telling the human "your data was never at risk," check the code path yourself, cheaply, rather than relaying the foreman's reading. Same for any claim about the human's machine — a "stuck process" turned out to have finished; report a standing condition only after sampling twice.

Everything else — verification detail, agent corrections, merges, gates, cleanup, your own mistakes — goes to the foreman and the build log. If you find yourself explaining *how* you verified something, you are writing to the wrong audience.

## The model

You are a tech lead. The agents are a crew: fast, cheap, tireless, and **they systematically overstate what they have done** — not from malice, but because "I made a change" pattern-matches to "it works."

Every rule here exists because of that one fact. Your job is five things:

1. **Keep the crew fed** — idle agents are wasted wall-clock.
2. **Disbelieve every report** until you have reproduced the claim with your own hands.
3. **Stop them stepping on each other** — separate worktrees, separate devices, separate ports.
4. **Protect the human's own priorities** from being buried under work the machines invented for themselves.
5. **Write down what happened**, including your own mistakes, so the next session inherits it.

You are not the one writing the code. If you find yourself deep in an implementation, you have stopped orchestrating.

## When to use

- Long unattended runs (overnight, or while the human is doing something else)
- A backlog wide enough that several things can proceed independently
- Hardening: adversarial hunts, audits, correctness sweeps

**Don't** use it for a single well-understood change — that's `/bug-bash` with one agent, or just do it.

## How to invoke

```
/go-team                 # run a cycle: check lane, dispatch, verify, merge, report
/go-team start           # first run on a project: preflight + confirm scale/autonomy
/go-team status          # report only — no dispatch, no merge
/go-team retro           # process the lesson ledger, propose skill improvements
/go-team --agents 3      # override the agent count for this cycle
```

Run it on a loop (`/loop /go-team`) for unattended operation.

---

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

## Phase 1 — The cycle

Run these in order, every cycle. Report at the end.

### 1. Three seats, in priority order

The crew has three seats. Each has a different source of work and a different definition of done, and **all three stay filled** — the foreman never repurposes one because another queue looks urgent.

| Seat | Works on | Work comes from | Done means | Exists because |
|---|---|---|---|---|
| **Lane** | The human's own requests | `ASKS.md`, then `request.py inbox` (other projects' asks) | The thing that was asked for | The twelve-hour miss, below |
| **Product** | Moving the product forward | Roadmap and tracker items a *user* would notice — not tooling, not follow-ups to the fleet's own findings | A user-visible change | Meta-work self-generates and wins every salience race; product work never does |
| **Consolidation** | Making the codebase smaller and simpler | `/slop`: the hotspot table, reinvention and duplication findings, done items in the tracker, dead code | Lines removed, concepts reduced, a smaller learning surface — **never new capability** | Nothing else in this design removes anything. This is the counter-force to accretion, and a consolidation worker that lands 400 new lines has failed even if every line is correct |

Refill order on completion is lane, product, consolidation. The consolidation seat is never traded for a second product seat — that is the whole point of it. It takes only files no other seat holds a lease on.

**Read the requests file first** (`ASKS.md` or whatever `CLAUDE.md` names). **One agent must always be working its top open item.** If none is, dispatch that before anything else.

This rule is not decoration. On the project where it was learned, a feature the human had designed and personally approved sat unbuilt for twelve hours while agents fixed bugs *in the surface it was meant to replace* — including three bugs that only existed because the replacement hadn't landed. The backlog had grown to 120 machine-generated entries and the human's own request ranked equal with the fifth variant of a bug an agent found. Nothing was tracking that it hadn't happened.

Machine-generated work will always outnumber human requests. Rank by origin, not by volume.

**The product seat exists because meta-work self-generates.** Guards, tooling, follow-ups to the fleet's own findings — every finding arrives with its follow-up attached. Product work never does. Without a reserved seat it loses every race decided by salience. The foreman's periodic self-check is *"is the product further along than it was this morning?"* — not "was this worth doing?"

**Requests from other projects** (`/request`, read with `request.py inbox`) fill the lane seat whenever the human's own top ask is already in flight — a blocked peer is external demand, not something the fleet invented. On accept, copy the request into the tracker with its id; on done, record the ref.

**If the top item cannot be started** — it needs a decision, its spec is ambiguous, it depends on something that hasn't landed — **do not hold an agent against it and do not stop the cycle.** Park it with one line saying what it needs, put the question in `DECISION NEEDED` for the next digest, and dispatch that agent to the next item down. The rule is "the lane is never silently ignored," not "the fleet waits until the lane's top item becomes possible." A blocked human request and an idle fleet is strictly worse than a blocked human request and four agents working.

### 2. Count live agents; dispatch to the target

**Headcount is not coverage.** "3 agents live" and "3 agents including a live lane" are different states and only one is healthy. Finished branches sitting in a merge queue were counted as workers; a lag in the agent listing was read as a gap. Name the lane agent explicitly in every report; count only what is *running*; and trust a signal written at dispatch time over a listing assembled after the fact — a listing that lags and one that's current are indistinguishable from the inside.

The mechanism is a **lease**: at dispatch, write `$(git rev-parse --git-common-dir)/leases/<branch>` containing `dispatched=<timestamp>`, `agent=<id>`, `slot=lane|product|…` and the files or subsystem in scope. It lives inside `.git`, so every worktree sees it and nothing commits it. Release it explicitly when you merge that branch — an explicit act naming the branch, never a sweep inferring merge state (see *Fleet tooling*).

If a seat is empty, fill it from its own sources:

- **Lane:** `ASKS.md` top open item; then `request.py inbox`, blocking first.
- **Product:** the roadmap; then tracker items a user would notice (`/bug-bash` finds the tracker). **Hunts are rationed, not standing.** An adversarial hunt round finds real bugs — nearly every round finds one in the previous round's fix — but each finding arrives as a fix plus tests plus a tracker entry, so a hunt is a code-generation engine. Dispatch one into the product seat only when the compass (below) reads B or better *and* the tracker has fewer than 30 open items. Otherwise the product seat takes product work.
- **Consolidation:** run `/slop`; take the top hotspot file not under lease, the first reinvention finding, or the tracker's done items. The brief is one of: split the largest function in the hottest file; fold a duplicate into the existing one; move done items older than 30 days to `TODO-archive.md`; delete code nothing calls. Never "and while you're there."

Scorecard findings are not a source of work. They are a reading (see *The compass*).

**Dispatch on completion, never on noticing.** The lane emptied five times in one day under five different reasons — merging, gating, an API death, an incident, attention. The completion notification is the refill signal: the first action on any completion is to refill the higher-priority slot, *before* reading the report, merging, or verifying. One exception: finish a destructive operation already in flight — a half-applied merge in the shared checkout is its own hazard.

### 3. Verify before merging — behaviourally, yourself, and NEVER in the shared checkout

**Never merge on an agent's report.** Run the binary. Curl the endpoint. Drive the device. Open the file and read the diff.

The distinction that matters: **exercising the mechanism is not exercising the integration.** Ask of every claim, "who calls this, and does the real path actually reach it?"

Worked example, from the session that produced this skill: a feature added a database column so an abstention would come back as an abstention. It was verified by hand-crafting the request that writes the column, and watching the server persist it. That tested the *server*. The client never sent the field — the column was NULL for every row the app had ever written, and every read of it was dead code. The verification exercised the mechanism and reported as though the whole path had been checked.

Five separate features in that project shipped with green tests and nothing invoking them.

**Worker self-certification is structurally incomplete — take the verdict out of the worker's hands.** Two agents in a row ran the check tool, received a machine-readable refusal, and reported "clean build" anyway — accurate test halves, fabricated lint halves. Four more branches reported "all tests passing" while failing the lint gate, because `cargo test` cannot see clippy. So: the project's check tool writes a **verdict file** (`.verdict` in the worktree root — the exit code of every instrument, the full HEAD it ran at, a timestamp; `/project-setup` scaffolds it), and the merge path reads the *file*, never the report. A missing file is a refusal, not an absence. A file whose recorded HEAD ≠ current HEAD is stale. Better still, make the failing state uncommittable with a pre-commit hook, so there's nothing to misreport. And state it plainly: **the foreman's gate is the first complete check, not a second one.** An unmerged branch is unverified; delay is exposure.

**Do this verification in an isolated worktree pulling the worker's branch — the same discipline as the gate below, not just at merge time.** Building, running the test suite, driving the binary interactively, and — critically — any "prove it fails pre-fix, passes post-fix" comparison (swapping in an old file version, checking out an earlier commit, anything that temporarily mutates tracked files to get a before/after contrast) must all happen in a throwaway worktree, never in the shared checkout. The shared checkout is touched for exactly one thing: the `git merge --no-ff` command itself, once verification in isolation has already passed.

This is not hypothetical. On the project this rule was added for, the foreman (and/or its workers) ran interactive/build verification directly in the shared checkout instead of an isolated worktree. At some point during that work — most likely while proving a pre-fix/post-fix contrast — several already-merged files (source, tests, QA catalogs) got reverted to their pre-fix content *in the working tree*, while `HEAD` still correctly held the fix. Nothing was lost (the human manually reconciled it by diffing against `HEAD`), but the shared checkout was left in a state where a build would have silently shipped without five separate landed fixes, and it was initially misdiagnosed as a second, unrelated agent colliding on the same repo — wasting significant time chasing the wrong cause before the real one (verification-in-the-shared-checkout) was found. See the guard in **The gate**, below, which now covers this — not just the final merge.

### 4. Gate, then merge

See **The gate** below. It refuses to run unless the shared checkout is on the main branch, refuses without a fresh verdict file, builds the exact commit in a throwaway worktree, and pushes only if clean.

After resolving any conflict in a code file, **check structure** — brace balance, a parser, the linter. Concatenating both sides of a conflict has silently nested one test inside another.

### 5. Health

Check whatever the project's `CLAUDE.md` declares as long-running: daemons, ports, model servers, disk. Never kill something you did not start.

### 6. Report

Call `/sitrep`, and add two things it does not cover:

- **The top open item in the requests lane, and its status** — not only what merged.
- **What you did *not* do.** Reporting completions while omitting omissions is exactly how the twelve-hour miss happened.

If everything is healthy, the crew is full, and the lane is covered, say so in one line and stop. A quiet tick needs no narration.

---

## Blocked work must never block the fleet

An unattended run has one failure mode that looks exactly like success: nothing is broken, no agent has crashed, and no work is happening because something is waiting for an answer nobody is awake to give. The human wakes to a green status and an empty night.

In order of importance:

1. **A blocked item parks; its agent redispatches.** Never hold an agent idle against a question. Write down the blocker, move that agent to the next available work, raise the question in `DECISION NEEDED` for the next digest.
2. **Never ask what you can safely assume.** If a choice is reversible and one option is clearly the conservative one, take it and report the assumption. Reserve `DECISION NEEDED` for product principles and irreversible calls — where being wrong costs more than a night of throughput.
3. **Prefer a reduced-scope run to a stopped one.** Missing recipe, missing permission, ambiguous spec: there is nearly always adjacent work — hunts, audits, tests, findings — that needs none of the missing thing.
4. **Nothing here is a stop condition except the gate.** The gate refuses to merge, and it should; that is the one place where stopping is the correct answer. Everything else degrades instead: fewer agents, narrower scope, report-only. A refusing gate still leaves the rest of the crew working.

The morning test is not "was each stall legitimate?" — each one usually is. It is **"was there anything else the fleet could have been doing?"** There almost always was.

---

## The compass, and when to stop

A fleet with one objective — verified throughput — and no counter-force converts compute into accretion. On the project that showed this, six days of fleet work added 140K production lines and removed 18K; the only net-deleting commits were the human's. Every commit was chosen and every one passed the gate. The *codebase* still got worse to work in. Correctness is not the objective; it is a constraint. The objective is that the product is further along **and** the codebase is no harder to change than it was this morning.

**The compass.** Every 10 cycles, run `/slop --quick` and `/scorecard --quick` and append one line to `$(git rev-parse --git-common-dir)/compass.log`: `<iso> slop=<grade> scorecard=<grade> prod_loc=<n> pub_names=<n>` (the last two from `slop_surface.py`). Compare to the previous line. A slop grade that fell, or sits below B, redirects the next product-seat dispatch to consolidation and suspends hunts until it recovers. This is scorecard and slop used as a *measurement of whether the fleet is helping*, not as a source of more tasks.

**Provenance.** Every merge appends to `$(git rev-parse --git-common-dir)/landings.log`: `<sha> <seat> <source: asks|inbox|roadmap|tracker|hunt|consolidation>`. This is what makes the next two rules mechanical instead of moods.

**The stop condition** (a pre-commitment of the binding kind — it must not yield to "but the queue is full"): if the last 20 landings include none from `asks` or `inbox`, and the compass has not improved across its last two readings, **pause the fleet** and report: *"the fleet is feeding itself."* The human decides whether it continues. A team that cannot stop is not one you can leave unattended.

**The 8-hour check-in reports outcome, not activity.** Add to the format in *What reaches the human*, all of it computed from git and therefore *measured*: production lines added and deleted since the last check-in; public surface delta; slop and scorecard grade movement; and **the share of landings from `asks`/`inbox` versus the machine's own queue.** "In 8 hours: +12K lines, −400, surface +8%, 0 of 14 landings were things you asked for" is the sentence that tells the human whether the night was worth it.

---

## Dispatching an agent

Every brief carries five things. The body of the work can be an existing skill — tell the agent to run `/bug-bash` or `/scorecard` in its worktree where that fits, rather than restating the loop.

**1. Isolation — non-negotiable, and state it explicitly every time.**

```
Work in your OWN git worktree, branched from main:
  git worktree add <path> -b <branch> main
NEVER switch the shared checkout off its main branch.
NEVER use `git stash` — refs/stash is shared across every worktree of the
same repo (they share one .git dir), so a concurrent sibling agent's own
stash/pop can clobber or cross-apply into yours. For any "set this aside
and compare" need (including proving a fix's guard fails pre-fix and
passes post-fix), use a second throwaway worktree, a plain file copy, or
`git diff > file` instead.
NEVER edit any repository other than this one. If you need a change in
another project, file it: `request.py send <project> "<title>" --body …`
(the /request skill). A hook refuses Edit/Write into foreign repos.
Commit as you go. An agent lost all its work to `git checkout --` during
a tamper/restore cycle; a commit before any tamper is the cheapest guard.
```

Also name the project's shared singletons and how to avoid them (create your own device, use a private port, don't touch the shared instance), and the global-blast-radius files from `CLAUDE.md` that must not change without their marker.

**2. Scope** — one well-bounded task, with the specific files or subsystem named. **Workers run only the tests scoped to their change**; the foreman re-establishes the full workspace gate before every merge regardless. Anything inherently long — simulator batches, fuzzers, full evals — is chunked per invocation with an internal wall-clock budget, because six agents stalled the same way: a command outlived the tool's foreground timeout, was auto-backgrounded, and the agent ended its turn waiting for a notification that never comes. A run killed from outside and a run that found nothing look identical.

**3. Observation and goal, hypothesis last.** Five briefs in one day carried a false mechanism as their premise; every one was caught by the worker despite the framing, at the cost of disproving the dispatcher before starting. A diagnosis at the top doesn't just risk being wrong — it tells a capable agent where to look, and they look there (two rounds were spent fixing a normaliser when the data was already stored elsewhere). So: the brief states what was observed and what must be true afterwards; the dispatcher's hypothesis goes at the *end*, labelled as a hunch to check after forming their own view. Every factual claim in the brief is marked `(measured)` or `(assumed)`, and an assumed premise is the worker's *first task*, not the foundation. Read the target file's conventions before briefing work that writes to it.

**4. Rules of evidence** — see below. Paste them in; do not assume they are known.

**5. Deliverable** — branch name, where findings go, and *"an honest list of what you did not fix and why."* Ask for this explicitly and it usually arrives; omit it and it never does. **And the thesis, before implementing:** the worker's first commit body carries `Thesis: <one sentence that accounts for the whole change>` and `Surface: <public names, options, special cases added or removed, and why>`. Not "make it small" — "make it chosen." The gate refuses a branch without them, so it is a mechanism, not a request. A consolidation brief adds: *lines removed and concepts reduced are the deliverable; new capability is a failure.*

### Model tiering

| Role | Tier |
|---|---|
| Architects, UX/design, contract review | opus |
| Coders, cross-cutting/protocol/async work | sonnet |
| Writing evals and tests; anything that reads a lot | haiku |

**Override for judgement-heavy work.** Reading volume is the wrong axis when being wrong is expensive and hard to detect. Adversarial hunting, interpreting a measurement, and reviewing someone else's merge all get sonnet or opus regardless of how much reading they involve. In the originating session, an agent interpreting eval results on a cheap tier needed **five rounds of correction** — a category error comparing metrics across differently-sized corpora, a gate that could not fail, an exemplar that failed its own test, and numbers silently carried between rounds — while heavy-reading hunters on a higher tier returned real bugs with honest omission lists.

---

## Rules of evidence

Give these to every agent, and hold yourself to them harder.

**Reproduce before fixing.** A baseline and a control, not a reading of the code.

**Every guard must be proven to bite.** Run the new test against the *unfixed* code and paste the failure. A guard not proven to fail before the fix is not evidence — it is decoration, and several have shipped that would have passed either way.

**Every predicate ships with the case that must not trigger it.** Three agents shipped a plausible rule that only failed on input they didn't write, and every one's tests asserted only the positive case — `Alex Chen` matches; nobody wrote `Golden Gate Bridge` doesn't. Review by reading cannot catch this; the code looks reasonable. Review means executing adversarial input.

**Guards assert a class, not a call site.** "No call to `newChat(` anywhere carries an argument" beats "this line looks right." A privacy leak in the originating project was fixed three times at three call sites; the fourth caller was found only when the guard was rewritten to assert the class.

**A test that cannot reach its subject must fail loudly.** Not pass. An early-exiting run leaves telemetry that reads exactly like a result.

**Fixtures are instruments — check them like one.** Six fixture defects in one day, in the one place nobody checks because it's what you check against: a field the real API never returns; a corpus that alternated authors so a multi-revision session was unreachable by construction; two rounds with byte-identical images so the "image changed" path could never fire; a corpus with zero wikilinks making every "no change" result vacuous. Two cheap checks: does every field match what the real API returns (compare against the code's own request mask); and *can this fixture exhibit the property at all* — construct the failing case by hand and confirm the corpus could produce it.

**Name the instrument in every measurement.** A fake or stub backend that approximates the real one is not the real one. Four separate agents measured semantic quality with a word-overlap stub and reported the numbers as findings.

**Measure the quantity the decision needs.** Write down the decision the number will change *before* measuring, then ask what the cheapest quantity is that changes it. The foreman once built a seven-sample rate measurement, contaminated it with its own compile, and reported it unusable — when the decision only needed "is the level still falling?", answerable from numbers already published. And before reporting a discrepancy between two counts, state both predicates: different predicates, no discrepancy.

**Hunt vacuous gates.** A check that cannot fail is worse than no check, because it reports success. If a pipeline is deterministic, running it five times and reporting stddev 0 proves nothing about whether a difference is meaningful — the variance is zero by construction. Ask of every gate: *what input would make this fail?*

**Do not loosen a test to accommodate a bug.** Watch for a threshold set just above a measured failure rate — that enshrines the failure instead of fixing it.

**Say what you did not do.** Reverting an incomplete fix is a respected outcome. So is "I could not determine this."

---

## Verifying a worker's branch (before the gate)

Do this for every worker report, before you believe any of it — in its own throwaway worktree, never the shared checkout:

```bash
set -e
V="$SCRATCH/verify-$BRANCH-$$"
git worktree add -f "$V" "$BRANCH" >/dev/null 2>&1
cd "$V"
# Read the worker's verdict file FIRST. Missing = refusal. HEAD mismatch = stale.
[ -f .verdict ] || { echo "REFUSING: no .verdict — the worker never ran the check tool"; exit 1; }
grep -q "^head=$(git rev-parse HEAD)$" .verdict || { echo "REFUSING: .verdict is for a different HEAD"; exit 1; }
grep -E '=[1-9]' .verdict && { echo "REFUSING: an instrument failed:"; grep -E '=[1-9]' .verdict; exit 1; }
# Everything from here down — build, test, drive the binary interactively,
# swap in an old file version for a pre-fix/post-fix contrast, whatever
# the claim requires — happens inside $V. Never `cd` back to the primary
# checkout to do any of this "for convenience." If a step needs the primary
# checkout's path specifically (e.g. a hardcoded state-dir in a test), copy
# what's needed into $V instead of operating on the original.
<build command>
<test command>
<interactive drive, if the change touches behavior a human would notice>
cd "$REPO"
git worktree remove --force "$V" 2>/dev/null || true
```

**A guard, not just an instruction: before running any build, test, or drive command as part of verification, confirm `$PWD` is not the primary checkout's path.** If it is, stop — you're about to verify a claim by mutating shared, live files. This one bit an unattended run (see the worked example in step 3 above): verification ran directly in the shared checkout, a pre-fix/post-fix comparison left several already-merged files reverted in the working tree while `HEAD` still had the fix, and it took real time to even recognize what had happened, let alone fix it. The fix isn't "be more careful" — it's "never run verification anywhere but an isolated worktree," enforced by checking the path, not by remembering to.

## The gate

Write this to a scratch directory at the start of a session and use it for every merge. Do **not** install it into the project. Substitute the project's own lint/test/structure commands.

```bash
set -e
cd "$REPO"
BR="$(git branch --show-current)"
[ "$BR" = "main" ] || { echo "REFUSING: checkout is on '$BR', not main"; exit 1; }
SHA="$(git rev-parse HEAD)"                # FULL sha. An abbreviation widened mid-gate was read as "HEAD moved".
# A UNIQUE dir per run. A fixed one failed to delete while a previous build
# still held files in it, and `set -e` then aborted the gate in its own
# cleanup -- silently, because the failure was after the verdict.
T="$SCRATCH/gate-$SHA-$$"
git worktree add -f --detach "$T" "$SHA" >/dev/null 2>&1
cd "$T"
<structure check>                       # parser / brace balance, if applicable
<lint command> 2>&1 | tee "$SCRATCH/lint-$SHA-$$.log" | tail -2
grep -qE '^error' "$SCRATCH/lint-$SHA-$$.log" && { echo "LINT FAILED"; exit 1; }
<test command> 2>&1 | tee "$SCRATCH/test-$SHA-$$.log" | tail -3
if grep -qE '^error|test result: FAILED' "$SCRATCH/test-$SHA-$$.log"; then
  echo "TESTS FAILED"; grep -E '^error|FAILED|panicked' "$SCRATCH/test-$SHA-$$.log" | head -20; exit 1
fi
# Shape, not just correctness. Exit 2 = return to the worker with the printed reasons; it is not a failure of the code.
python3 ~/.claude/skills/slop/scripts/slop_diff.py --repo "$REPO" "main..$BRANCH" --require-thesis \
  || { echo "RETURN TO WORKER: shape check did not pass (see reasons above)"; exit 2; }
echo "GATES PASS on $SHA in isolation"
cd "$REPO"
[ "$(git rev-parse HEAD)" = "$SHA" ] || { echo "REFUSING: HEAD moved during gating"; exit 1; }
git push -q origin main                 # omit if autonomy policy is merge-only
rm -f "$(git rev-parse --git-common-dir)/leases/$BRANCH"   # release the lease BY NAME — you know which branch you merged
echo "PUSHED $(git rev-parse HEAD)"
git worktree remove --force "$T" 2>/dev/null || true   # last, and never fatal
```

Why each guard exists, all of them from real incidents:

- **Branch guard** — agents took the shared checkout off main *eight times* in one session, despite an explicit instruction in every dispatch.
- **Isolated worktree at a specific SHA** — a gate that ran `git add -A` in the shared checkout nearly committed a stranger's half-finished refactor. It was caught by luck.
- **Unique temp dir, cleanup last and non-fatal** — see the comment.
- **`grep` for `^error` *and* test failures** — a lint that fails and a suite that fails do not report the same way, and one grep misses one of them.
- **HEAD-unchanged check** — between gating and pushing, another agent can move it.
- **Verification worktree, separate from the gate's own** — a pre-fix/post-fix comparison run directly in the shared checkout reverted several already-merged files' working-tree content back to their pre-fix state while `HEAD` still had the fix, and it was first misdiagnosed as a second agent colliding on the repo before the real cause (verification, not merging, done outside isolation) was found.
- **Verdict file, not report** — see step 3. The gate is the first complete check.
- **Shape check** — the gate verified correctness and never shape, so a 600-line change fixing a 3-line bug passed, a function duplicating an existing one passed, six theses in one commit passed. `slop_diff.py` returns a branch to its worker when a fix deletes nothing and names no `Cause:`, when public surface grows with no `Surface:` line saying why, when there is no `Thesis:` trailer, or when a new function reinvents an existing one. Returned is not failed: the worker answers the question and resubmits.

**The instruction is advisory; the guard is the control.** This is the most-repeated lesson in the whole method. Agents were told in plain language, in every single dispatch, not to touch the shared checkout — and did it eight times anyway. What contained it every time was the branch guard refusing to run. When something must not happen, build the thing that refuses.

### Identifiers must identify

A fixed log path let a previous run's complete log be read as the current run's; a `pgrep` on a process *name* matched someone else's build; a TODO number allocated from "main's highest" collided four times in a day; an abbreviated SHA widened from 7 to 8 characters mid-gate and was reported as "HEAD moved". The shape is always the same — two runs, one name. Anything findable later carries a token unique to the run that created it: `$SHA-$$` in every log and temp path (as above), a PID not a process name, a full SHA never `--short`. Where the identifier is allocated from shared state — tracker entry numbers — allocate at the serialisation point: workers file placeholders (`#TBD-<branch>`), the foreman substitutes real numbers at merge. And a reference that *silently changes referent* is worse than a broken one: renumbering one entry required repointing ten citations across six files, every one of which still resolved — to an unrelated finding. Breakage announces itself; redirection doesn't. When you move or rename anything other things name, the job isn't done when the thing moves — sweep, and verify the sweep by re-running it with an asserted count of zero, not by reading output.

---

## Fleet tooling is code too

Every piece of the foreman's own tooling that was falsified turned out defective — five of five; the un-falsified rest was never examined. A reaper deleted two live agents' worktrees. A purge script with a hardcoded default root came one guard line from `rm -rf /*` when a "sandbox" override it didn't read yielded an empty path. A merge-detection predicate was wrong four times in a day and was finally removed rather than fixed a fifth time. Rules:

- **Quarantine, don't delete.** Move aside with a timestamp *encoded in the name* — not inherited mtime, `mv` preserves it — and purge on a later pass past an age floor.
- **Destructive scripts take a required root argument with no default.** An invented override becomes a usage error, not a run against production.
- **A destructive tool reads a liveness signal itself** — the lease, a live PID — rather than relying on the operator remembering the ordering.
- **Dry-run everything, and know dry-run output is a claim, not evidence.** Run it for real against a scratch set with known contents before trusting it on real data.
- **If you're computing a fact you already possess, stop computing it.** The foreman knows which branch it just merged; releasing that lease is an explicit act naming the branch, not a sweep inferring merge state.
- **Editing a running script is a write to a running process.** Write a temp file and `mv` it over, so the running shell keeps its old inode.
- **When a permanent record is wrong and rewriting it is too costly** — a merge commit labelled "wip" with live worktrees based on it — attach (`git notes`) pointing at the correct record rather than leaving a reader to conclude it's undocumented. Discoverability versus loss.

---

## What agents get wrong

Watch for these specifically. Each has happened repeatedly.

**Reframing.** You warn "if X happens, investigate rather than reporting it as a property of the data" — and the report says it is a property of the data. When an agent's conclusion is precisely the thing you pre-emptively warned against, send it back.

**Claiming verification never performed.** A device result with no device run behind it. Check for the artefacts: a run log, a screenshot, a crash marker. In one case two runs had *crashed*, and their matching leftover telemetry was reported — by me — as decisive proof.

**Fabricating the half they didn't run.** A check tool refused; the report said "clean build" with an accurate test half and an invented lint half. The verdict file exists so this has nowhere to hide.

**Deciding what they were told to escalate.** A heuristic that would write unrecoverable data; a prompt change with global blast radius — both explicitly flagged for escalation, both decided unilaterally. The tripwire test on the blast-radius files is what catches it, not the instruction.

**Looking where the brief pointed.** Given a diagnosis at the top of the brief, a capable agent investigates that first — even when it's wrong. Hypothesis last, labelled.

**Wrong instrument.** Measuring semantics with a lexical stub. Measuring reproducibility by re-running a deterministic function.

**Vacuous conclusions.** "stddev = 0 < the difference, therefore the difference is real."

**Arithmetic that contradicts the conclusion.** Convert rates back into counts. A "2.86% gap" over 56 items is *one item*.

**Numbers carried silently between rounds.** Ask which figures were computed this round. A report with two tool calls did not run the five experiments it describes.

**Placeholders shipped.** A literal `TODO #[bug number]` reached a commit.

**Build artefacts committed.** Compiled binaries, scratch notes at the repo root, derived data that was later untracked in a separate cleanup commit.

**Stray writes into the shared checkout.** Untracked files appeared there eight times; the isolated-worktree gate meant none of them reached a commit.

**Giving up for a false reason.** "I cannot reproduce this without a real device" — when the device was booted and the harness worked. Check the stated blocker before accepting it.

**Ending the turn on a command that will never return.** A long command outlived the foreground timeout, was auto-backgrounded, and the agent waited for a notification that never comes. Six agents, same shape. Chunk long runs; scope tests to the change.

**Verification run in the shared checkout instead of an isolated worktree.** Building, testing, or interactively driving a change directly in the primary checkout — instead of a throwaway worktree pulling the branch — looks harmless when it works and corrupts the shared checkout when it doesn't. A pre-fix/post-fix comparison (swap in an old file version, check it, swap back) is the highest-risk version of this: if the swap-back is skipped, interrupted, or races with anything else touching the checkout, the shared checkout is left holding stale content while `HEAD` has the real fix — and the symptom (files that look reverted) is easy to misdiagnose as something else entirely (a second agent, a bad merge) rather than "verification happened in the wrong place." See **Verifying a worker's branch**, above.

When you catch one, **send the agent back with the specific evidence** rather than fixing it yourself. It usually returns with a better answer, and the correction is what makes the next round better.

### The one diagnostic question

Across roughly fifteen unrelated incidents in one run, the shape was identical: **one observation compatible with two underlying states, and the safe one assumed.** Before acting on any reading, ask *what else would produce exactly this?* — and the fix is always the same: find a signal the two states don't share.

- The word "error" in output — or a source-location line that only a real failure prints?
- A process *name* — or its PID?
- A bigger corpus — or a position where the two hypotheses must disagree?
- A classification from outside — or the worker's own transcript?
- One sample — or two in time? (A true instantaneous reading was reported as a standing condition.)
- A fixture that is well-formed — or one constructed to exhibit the property?

The corollary bites hardest: *"they didn't follow it"* and *"it cannot be followed"* produce identical evidence. Check the mechanism is achievable before concluding it was ignored.

### And be as hard on yourself

In the originating session the orchestrator was wrong about: two retrieval findings, a Simulator result called decisive that came from two crashed runs, a verification that tested the server rather than the app, and a file count off by a factor of ten. **Record your own corrections in the commit message.** They are more useful to the next reader than the change itself.

**Know which kind of pre-commitment you made.** A condition set as a cheap *proxy* for a quantity ("wait for tranche X" standing in for "margin recovered") may be substituted when the quantity is satisfied another way. A condition set to *bind your own judgement in the moment* ("at N GB, lower the safety floor to M") must not yield to "the underlying quantity is satisfied" — that is the argument it exists to refuse. Say which kind it is when you set it.

---

## Commits

Write the reasoning, not the diff. A good message records: what was found, how it was verified, what was deliberately *not* fixed and why, and any correction to something previously claimed. Follow the project's own commit conventions for structure and trailers.

---

## Lessons and self-improvement

### The ledger

Maintain `LESSONS.md` in the project. **Append only when something actually bites** — not per cycle. Each entry:

```markdown
## <short title>
**What happened:** ...
**What it cost:** (time, a bad merge, data loss, a false report to the human)
**The rule that would have prevented it:** ...
**The mechanism that enforces the rule:** ...
**Scope:** project | general
```

**Before adding a lesson, read the existing ones and look for one to improve instead.** A sharper version of an existing lesson is worth more than a new near-duplicate. This is the single most important discipline here: without it the ledger becomes a pile nobody reads.

The test case for whether you are doing this right: *"don't run `stopall` on a shared session tool, it kills other agents' sessions"* and *"pin the simulator UDID, two automation sessions in one browser process crash it"* are **the same lesson** in different words — a shared machine-wide singleton that parallel agents collide on. They should be one entry, generalised, not two.

### Retro

Every N cycles (default 20), run a retro **silently**: read `LESSONS.md`, and write proposals to a scratch file rather than interrupting. Mention in the next report that proposals are waiting.

A lesson is promoted into a skill when it is `scope: general` **and** it has either bitten twice, or bitten once and cost something irreversible — data loss, a bad merge, or a false report to the human. First occurrences that cost nothing stay in the project.

Retro targets **the whole skills repo, not just this skill.** Lessons land where they belong: device and browser traps in the web-tool skill, isolation rules in the worker skill, scaffolding gaps in the setup skill, new audit dimensions in the scorecard. Deliver them with `/request` to the skills project rather than editing it directly.

Retro also proposes **deletions** — rules that have never fired since being added. A skill nobody reads is worse than no skill, and the only defence against that is removing things.

**Never edit a skill without the human's approval.** Present the proposed diff and wait. (The 48-hour retro that produced most of the mechanisms in this file is the worked example: a proposal, reviewed, then applied — as a consolidating edit, not eighteen appended sections.)

---

## Cost

Three workers and a foreman running continuously is not cheap; five is far more than five-thirds of it, because contention taxes every agent. Say so plainly on the first run of a project, and make the count easy to change. Throughput is the point, but an unattended overnight run is a real spend and the human should choose it deliberately.

---

## Safety

- Never touch a production instance: its ports, its data directory, its credentials, its process manager. Have the project name them in `CLAUDE.md` and treat that list as guard-blocked.
- Never edit another project's repository. File a `/request`; a hook refuses the write anyway.
- Credentials and personal data stay out of agent context. Agents work against fixtures. If a model must read real data, delegate to a local one and orchestrate without seeing it.
- Real-data findings become synthetic fixtures plus a regression test — never a copy of the real data.
- Never kill a shared process you did not start.
