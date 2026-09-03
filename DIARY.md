# Engineering Diary

Latest entries first. Record significant decisions, architecture changes, and non-obvious context.

---

## 2026-09-03 — /slop on two 100%-AI repos: the thesis holds in one, and the mechanism isn't what we expected

Joe suspected zepto and sidebrain — both entirely AI-written, with less manual review and autonomous agent loops — would grade worse than websocketd. One did. Neither failed the way he predicted.

**Zepto (458 commits, 7 months, Perl): B.** No hand-written era, so the trailer split is really early-AI vs late-AI, and the production add:delete ratio *improved* from 8.5:1 to 3.3:1. Fix commits are 35% of history — but that's the methodology: an adversarial QA loop files `QA-REG-NNN` bugs and fixes them. The three largest zero-deletion "fixes" were each a one-to-twelve-line production change with a stated root cause under 200–400 lines of regression tests; one explicitly overturned its own hypothesis ("not a Shift+Tab/InputParser bug at all"), and another debunked the reported bug as a screenshot-tool artefact and fixed a narrower real one found along the way. Chosen, all of it. What the numbers *did* locate: three god files. `Renderer.pm` (6,226 lines, 14 late-era fixes), `Editor.pm` (5,519, 15), `Commands.pm` (1,636, 6) absorb most of the fixing and are growing 18–20% a quarter — `Commands.pm`'s anonymous closures, the command table itself, went 8 → 36; a chain of three consecutive `Renderer.pm` fixes turned out to be three different bugs, not one re-fixed — a hotspot, not sediment, but the place sediment will form. Refactor moves: 9 in 458 commits. The command palette grew 44 → 64 commands while `FEATURES.md` grew one line and has been touched three times in seven months.

**Sidebrain (1,054 commits in six days, Rust, agent fleet): C+.** The commits read are chosen — the empty-query unification states its decision and reasoning; a "hunting round" commit is an honest audit record. But the *system* is accreting at fleet speed: 140K production lines added, 18K deleted, in six days. `brain-retrieve/src/lib.rs` is 5,297 lines and `storage.rs` 4,637 — but 52% and 64% of those are *inline test modules*, so the production halves are moderate; the real reader-load finding is eight functions over 100 lines in `lib.rs`, the longest 448 (`compute_relevance_verdict`), 322 and 272. The server's `tests/api.rs` is 19,740 lines and 318 functions in three modules. `TODO.md` is 34,872 lines and 2.1 MB — roughly 390 done-markers against 18 OPEN, never pruned. The one fix I read pastes an identical three-line guard into three functions and adds five copy-pasted tests for it. And the fleet leaves artefacts a reconciliation role has to clean: the same round-48 commit reached main by two branches; TODO entries duplicated by merges were de-duplicated in three separate later commits; 5K lines of derived data were committed then untracked; a 42K-line corpus merge was reverted. The 184 untagged commits (which could be Joe or the foreman — every commit's author is Joe regardless) are net-*deleting*, and that revert is most of why. On the other side of the ledger, `ARCHITECTURE.md` machine-checks its own "Built:" claims with a test, every citation verified to exist — the strongest theory-holder mechanism I've seen anywhere — and `DECISIONS.md` records 28 decisions with inline self-corrections, though #12 has become a 600-word paragraph.

**So the mechanism differs from Joe's description.** He expected guards-around-symptoms. What's actually there, in the fleet-run repo, is that *nothing is ever folded back or pruned* — chosen code piling up in god files, a god test file, a god tracker — because no agent's brief is ever "make this smaller," and the human's role has become deletion. Websocketd, with a human reviewing every merge, had the same zero-refactor count but a flat surface. The variable isn't AI authorship; it's whether anyone is paid to remove things.

**Tooling changes from these trials:** a per-file fix-hotspot table (the pair-chain list was noise; hotspots locate the sediment); duplicate-landing detection (same subject and timestamp, different parents); lockfiles added to the registry exclusions; a warning when history is shorter than the churn window (sidebrain's six days made the 14-day churn metric meaningless). Skill notes: fix *rate* reflects methodology; read a fix chain before calling it sediment; measure god files and trackers directly; attribution is by trailer, not author; and three confident wrong numbers from three portability quirks in two days: `grep -v _test` filters lines not files; zsh treats `$REV:path` as a modifier; and macOS's BWK awk doesn't know `\s`, so `^\s*fn` anchored to column 0, saw only top-level functions, and turned an entire `impl` block into a phantom 2,277-line function. The CLAUDE.md rule — measure in Python, not shell — vindicated a fourth time; the fix-hotspot grep was also matching "fixture", which the script's subject-only word-boundary regex doesn't.

---

## 2026-09-03 — /slop: measuring unchosen code, and a first trial that argued back

Joe described a feeling about his long-lived open-source projects since AI started writing most of the code: sometimes good, sometimes "it just doesn't feel right," and hard to articulate. When he wrote by hand, the sheer cost forced him to plan, to pick the highest-leverage change, and to write for a reader. With AI the pattern is fix → tons of code → didn't work → tons more code.

The articulation we landed on: **hand-written code is the residue of understanding; slop is the residue of attempts.** Every absence in hand-written code was a decision (no null check = "I know this can't be null"). Slop has no absences — every guard that *might* be needed is present — so a reader can't tell what matters. Fix-by-addition is the locally optimal move when the reward is "did the error go away," which is why it's the signature. Naur's *Programming as Theory Building* is the deepest frame: the product is the theory in someone's head, and Joe was that someone.

**The correction that shaped the design.** My first cut of signals leaned on volume — "smallest diff," "single-implementation abstraction is a smell." Joe pushed back: he intentionally makes big changes, and intentionally creates one-implementation seams when he anticipates variation. He values small surface area and composability, not small diffs. So the axis is *surface area and articulability*, not size. Slop is **unchosen** code; the test is *could the author say why?* A 500-line refactor with one thesis passes; a 50-line fix with three theses doesn't. This became the skill's central rule and its "What this skill does NOT penalise" section.

**Research backing** (GitClear 2026: refactoring down 70%, duplication up 81%, error-masking constructs up 47%; a 302K-commit study: 22.7% of AI-introduced issues never fixed; METR: experienced maintainers 19% slower while believing they were 20% faster; the "Explanation Gate" study: requiring people to explain AI changes before merging halved later maintenance failures). The Explanation Gate became `/slop --explain`.

**Design.** A new skill rather than a scorecard dimension, because slop is a *trend over history* (different data source: `git log`, not the tree) and because the highest-leverage place to catch it is *pre-merge on a branch*, which scorecard structurally can't do. Four tiers: articulability decides; surface area decides; history trends are evidence; classic smells only annotate. A Python script computes the history signals and splits hand-written vs AI-attributed eras from commit trailers.

**The trial on websocketd argued back, which is the point.** 453 commits, 2013→now, 110 AI-attributed — a natural experiment. Headline numbers looked like the thesis: add:delete 2.4:1 → 7.5:1, refactor moves 17 → 0, median commit 13 → 44 lines. Then reading the flagged commits: every one had a stated, load-bearing reason (why removal beats escaping; why panic beats degrade; why a separate go.mod). Exported API went 23 → 24 names while code grew 60% — flat surface area. DIARY.md and LESSONS.md are exactly the theory-holder record Naur would want. The scary 7.5:1 was **86% tests, docs and tooling**; the production-code ratio was 1.97:1 in *both* eras — identical. Grade: not slop. The honest yellow flags: zero refactoring in 110 commits, and two commits bundling several theses (one lists six fixes in its subject line).

Three things the trial fixed in the tooling: changelogs and bug-registry files are touched by every fix *by design* and were inflating fix-of-a-fix chains — now excluded by share-of-fixes and by name; additions must be split production vs non-production before the ratio means anything; and two measurement traps worth recording because both produced confident wrong numbers — `grep -v _test` filters lines not files (it counted `TestXxx` as exported API, "tripling" it), and zsh treats `$REV:config.go` as a `:c` modifier.

---

## 2026-09-01 — Split /delegate into 5 skills; image panel + jury; bash → Python/Perl

Split the single `/delegate` skill into five standalone ones (`delegate-image`, `delegate-sec`, `delegate-private`, `delegate-review`, `delegate-bulk`) — Joe wanted each surfaced directly in `/` autocomplete rather than buried as an argument inside one umbrella command.

Along the way, ran a real benchmark: generated the same 4 prompts (2 logos, 2 photorealistic scenes) across all 4 Gemini image tiers on OpenRouter, had Claude and Kimi (blind, model identity hidden) critique and rank each, and published the comparison as an artifact gallery. Result was genuinely useful and a little surprising — price didn't track quality. `gemini-3.1-flash-image` (mid-tier, ~$0.067/img) won more blind rankings than `gemini-3-pro-image` (priciest, ~$0.138/img); only `gemini-3.1-flash-lite-image` (cheapest) was a consistent loser. `delegate-image` now defaults to a **3-model parallel panel** (flash, nano-banana 2.5, pro — dropping flash-lite) plus **two independent judge models** (Kimi K2.5, GLM-4.6v — different lineages from the Google generators and from each other) that each critique and pick a favorite. Joe generates images rarely enough that 3x the cost (~$0.24/prompt) is immaterial to him, so the panel is the default, not an opt-in.

A real integrity bug turned up building the judge step: `kimi-k2-thinking` has no vision support, but instead of erroring it fabricated a plausible-sounding critique from the model names embedded in the filenames alone. Caught it because the critique for one image was suspiciously specific for a "blind" test, and confirmed via the model catalog (`images: no`). Lesson embedded in the skill: verify a judge model actually has vision (`pi --list-models` shows `images: yes`) and sanity-check its critique cites real visual specifics, not generic praise — a model can return a confident, wrong answer instead of admitting it can't see the image.

Also hit a genuine bash portability bug while building the throwaway benchmark driver script: `declare -A` (associative arrays) silently failed because macOS ships `/bin/bash` 3.2, which doesn't support them — the script exited on "unbound variable" before generating anything, 4 background jobs in a row, no images produced. Root cause wasn't caught until reading raw task output instead of trusting the "exited 0" status. Fixed the immediate script by dropping associative arrays; fixed the class of bug by adding a CLAUDE.md rule: skill helper scripts must be Python or Perl, not bash, since both are always installed and portable, while bash isn't. Rewrote `delegate-image`'s panel-generation script in Python accordingly.

Other build notes: OpenRouter's per-request credit hold (reserving the model's full max-output-token capacity against the daily key limit) tripped a couple of times independent of actual balance — first on `gpt-5.6-sol` (128k max-out), then on `kimi-k3` (131k max-out) under concurrent judge calls. Worked around by preferring judge models with small max-output (`kimi-k2.5` at 4.1K) rather than trying to tune request concurrency.

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
