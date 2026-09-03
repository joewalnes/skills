---
name: slop
description: Audit a codebase or a branch for AI slop — unchosen code that grows the learning surface without adding leverage. Grades on articulability and surface area, with git-history trends as evidence and classic smells only as weak hints. Use on a repo to see whether it's accreting, or on a branch before merging.
argument-hint: [branch | rev-range | --explain | --quick]
---

# Slop

Hand-written code was expensive, and the expense did invisible work: it forced planning, forced holding the design in your head, forced choosing the change that gave the most leverage for the least disruption, and forced writing for a reader. AI made lines free, and every discipline the cost was silently enforcing vanished with it.

The result is two kinds of code. **Hand-written code is the residue of understanding. Slop is the residue of attempts.** Every absence in hand-written code was a decision — no null check means "I know this can't be null." Slop has no absences: every guard that *might* be needed is present, every fallback that *might* help is chained. It encodes uncertainty where good code encodes knowledge, and that is exactly why it's expensive to read — nothing was omitted, so a reader can't tell what matters.

**Slop is unchosen code.** That is the whole test. The signals below detect the absence of choosing.

## What this skill does NOT penalise

Get this wrong and the skill becomes a lint for "small," which is a different and worse thing.

- **A big change is not slop.** A 500-line diff that collapses three renderers into one has a single sentence that accounts for all of it, and the codebase has *fewer* concepts afterward. That is excellent. Size is not the axis.
- **A single-implementation abstraction is not slop.** A seam with one implementation is good when the interface is *smaller* than what it hides, it isolates a decision the author can *name*, and a second implementation would slot in without touching callers. Same shape on a diagram as "make it configurable"; opposite effect on the reader.
- **A fix that only adds lines is not automatically slop.** Sometimes a case was genuinely missing. The tiebreaker is whether the root cause is stated.
- **A high add:delete ratio driven by tests, docs and tooling is not slop.** Split additions into production code versus tests/docs/tooling before reading the ratio as accretion — the history script does this. Five hundred lines of regression tests behind a ten-line fix is chosen; five hundred lines of guards is not. (First trial: a 7.5:1 ratio that looked like sediment turned out to be 86% tests and tooling; the production-code ratio was 1.97:1 in both the hand-written and AI eras — identical.)

In every case the distinguishing question is the same: **could the author say why?** A change that can be explained, whose explanation accounts for the whole diff, is chosen. Grade intent, not volume.

## The hierarchy — what decides the grade

**1. Articulability (primary — decides).** Can the change be stated as one thesis, and does that thesis account for the whole diff? "Collapse the three renderers into one" — yes. "Fix X, and also handle Y, and add a fallback for Z" — that's three changes wearing one commit, none of them chosen. For a repo: can anyone say why each module exists?

**2. Surface area and composability (measurable proxy — decides).** The *learning surface* is everything a reader or caller must know: exported names, function parameters, config options and flags, modes and special cases in behaviour, the number of files you must open to understand one thing. Count it before and after. Good changes — large or small — hold it flat or shrink it. Slop only ever grows it. Composability: can the pieces be combined without knowing about each other, or does each new piece special-case the last?

**3. History trends (evidence — decides in repo mode).** These are the measured signatures of accretion, and `scripts/slop_history.py` computes them:
- **Fix commits that delete nothing** — the single strongest signal. A fix that understands finds the wrong thing and removes it; a fix that doesn't wraps the symptom in a guard.
- **Fix-of-a-fix chains** — the same file, two "fix" commits within two weeks.
- **Churn** — code rewritten within two weeks of being written.
- **Add:delete ratio** trending up; addition-only commits as a share.
- **Refactor share** (moves/renames) trending to zero; **legacy code** never revisited — the codebase grows only at its edges.
- **Big diff, trivial message** — "fix typo" touching 300 lines.

**4. Code smells (weak priors — annotate only, never decide).** Things that are *usually* unchosen. They raise a flag for reading; they do not move the grade on their own:
- Error-masking: broad `catch`/`except`, swallowed errors, `|| default` chains, optional-chaining everywhere, retries around things that shouldn't fail.
- Guards against states that cannot occur.
- Abstractions that grow the surface: an interface bigger than what it wraps, mode flags, options with one caller, a factory that makes one thing, "configurable" things never configured.
- Generic naming: `data`, `item`, `result`, `handle*`, `process*`, `utils`, `helper`, `manager`.
- Narrating comments (`// increment the counter`) versus load-bearing ones (`// see #123: X must precede Y because …`).
- Long methods, god classes, and the *modular mirage* — files split up but not semantically cohesive.
- Tests that mirror the implementation, assert a mock was called, or would pass if the code were deleted.
- New code that reinvents something already in the codebase instead of calling it.

## Modes

```
/slop                    # repo: history trends + a reading of recent flagged commits, graded
/slop <branch|range>     # diff: pre-merge audit of one change (go-team's gate uses this)
/slop --explain          # the Explanation Gate: you explain the change; the skill shows what you missed
/slop --quick            # one grade + three lines, for /scorecard's Accretion row
```

## Repo mode

1. **Run the script.** `python3 <skill-dir>/scripts/slop_history.py <repo>`. It splits history into a hand-written era and an AI-attributed era when it can (via `Co-Authored-By` trailers and similar markers) — that comparison, on the same codebase, is the most persuasive evidence there is. Use `--since` to narrow, `--split YYYY-MM-DD` if attribution is missing. Read the **production-code-only** ratio, not the headline one. Changelogs, docs and bug registries are excluded from fix signals automatically; check the exclusion line to make sure it caught the right files.
   When measuring surface area by hand, two traps from the first trial: `grep -v _test` filters *lines*, not files, so exported-name counts silently include `TestXxx` — filter the file list instead; and in zsh, `$REV:config.go` is a parameter modifier (`:c`), so quote it: `"$REV":config.go`.
2. **Read the flagged commits. Do not grade from the numbers.** For each zero-deletion fix and each fix-of-a-fix chain: `git show <hash>`. Ask the tier-1 question — could the author say why? Is there a root cause named, or a guard around a symptom?
3. **Sample the surface area.** Pick 3–5 substantive recent changes. For each, count the learning surface before and after: exported names, parameters, options, special cases. Note whether it grew, and whether the growth bought leverage.
4. **Check for a theory-holder.** Read `README`/`CLAUDE.md`/`DIARY.md` if present. Can the *repo* say why its modules exist? Does the architecture described match the architecture present?
5. **Grade** (rubric below), then write the report.

## Diff mode

For a branch or range, in this order — stop early if tier 1 fails badly:

1. **Thesis.** Write the one sentence that accounts for the whole diff. If you can't — if it needs "and also" — that's the finding. Check it against the commit messages.
2. **Surface-area delta.** Exported/public names, parameters, config/flags, special cases, files a reader must now open. Before vs after, as a short list. Did it grow? Did the growth buy anything?
3. **Composability.** Does the new piece special-case existing ones, or compose with them? Would a second instance of this thing require touching callers?
4. **Fix discipline.** If any commit calls itself a fix: what was deleted or changed, and is the root cause stated? A fix that only adds, with no cause named, is sent back — not failed, sent back with the question.
5. **Reinvention.** For each new function or type, grep for an existing one that does the same job.
6. **Smells** — annotate what you saw, clearly labelled as hints.
7. **Reader test.** Could someone understand this diff without knowing what the prompt was?

## `--explain` mode

The Explanation Gate, from the study that found requiring people to explain AI-generated changes before integrating them cut later maintenance failures roughly in half. Annoying by design; that's the point.

Ask the user for a paragraph: what the change does and why, from memory, without re-reading the diff. Then compare it against the actual diff and report **what the diff does that the explanation didn't mention** — those are the parts of their own codebase they don't currently hold a theory of. No grade. Just the list, and how large it is relative to the change.

## Grading

Grade the *codebase or change*, not the tooling that produced it. Human-written slop exists; AI-written chosen code exists.

- **A** — Every sampled change has one thesis that accounts for it. Surface area flat or shrinking over time. Fixes name causes and delete something. Refactoring is happening. A reader can reconstruct the author's reasoning from the code.
- **B** — Mostly chosen. Occasional additive fix or unexplained growth, but the architecture still says why it exists.
- **C** — Accreting. Fixes are guards. Surface area grows every change. Smells cluster. Someone still holds the theory, barely.
- **D** — Sediment. Fix-of-a-fix chains. Add:delete ratio climbing, refactor share near zero. Nobody can say why half of it is there.
- **F** — Dead in Naur's sense: modifiable, but not well. No theory-holder. Every change adds a layer.

**A change with one clear thesis and a shrinking surface cannot grade below B, however large.** **A change with no statable thesis cannot grade above C, however small.**

## Output

```
# Slop: <repo or change>   Grade: C

**Thesis test:** <one line — pass/fail and why>
**Surface area:** <grew / flat / shrank — the concept count, before → after>
**History (AI era vs hand era):** <the two or three numbers that matter, from the script>

## Chosen
- <things that were clearly decided, with hash/file:line — say why they pass>

## Unchosen
- <hash/file:line> — <what it is> — <the question the author couldn't answer>

## Hints (smells — not graded)
- <file:line> — <smell>

## What would make this pass
- <concrete, one line each>
```

## Rules

- **Read the code. Never grade from the script's numbers alone** — they are proxies and the script says so.
- **Name what was chosen, not just what wasn't.** A report that only lists faults teaches nothing about what good looks like here.
- **Cite hashes and file:line** for everything in Chosen and Unchosen.
- **Say what would make it pass**, concretely. "Name the root cause in `fc2d871`" beats "improve fix discipline."
- **Do not confuse your taste with the author's.** If the author states a reason you disagree with, that is chosen code you disagree with — a design conversation, not slop. Slop is code with no reason at all.
- **Big ≠ bad. One impl ≠ bad. Small ≠ good.** If you catch yourself grading on volume, stop and re-read *What this skill does NOT penalise*.

## Integration

- **`/go-team`** runs `/slop <branch>` in its gate. A fix that deletes nothing and names no cause goes back to the worker with the question — it does not fail, and it does not merge.
- **`/scorecard`** row 14, *Accretion*, runs `/slop --quick` and reports its grade, the same way Security cross-checks `/delegate-security-audit`.
- **Dispatch rule for agents**, upstream of all of this: *before implementing, state the thesis in one sentence and what surface area it adds or removes.* Not "make it small" — "make it chosen."
