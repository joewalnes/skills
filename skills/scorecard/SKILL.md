---
name: scorecard
description: Evaluate code quality with letter grades across multiple dimensions
argument-hint: [directory | --quick]
---

# Codebase Scorecard

Perform a comprehensive, critical third-party audit of a codebase and produce a structured scorecard with letter grades. This is a deep analysis, not a surface-level check.

## When to Use

- After completing a feature or major refactoring
- Code review preparation — run before submitting a PR
- Technical debt assessment — quantify what needs attention
- Onboarding to a new codebase — understand health at a glance
- Before/after comparisons — run before a cleanup, then after, to measure improvement

## How to Invoke

```
/scorecard                    # Full codebase audit of current directory
/scorecard src/               # Audit specific directory
/scorecard --quick            # Abbreviated audit (summary table only)
/scorecard --agents           # Agent-readiness audit only (second table, skip the code grades)
```

A full run produces **two** grades: one for the code, one for agent-readiness. They answer different questions for different audiences, so they get separate tables and separate overall marks — `Code: B / Agent-readiness: C+`.

## Analysis Process

You MUST perform thorough investigation before grading. Do not grade from vibes — read actual code and docs. Launch multiple exploration agents in parallel to maximize coverage.

### Phase 1: Reconnaissance (parallel)

Launch these investigations simultaneously using the Task tool with subagent_type=Explore:

**Agent 1 — Structure & Architecture:**
- Map the full directory structure, file counts, line counts
- Identify the build system, entry points, dependency graph
- Read README, design docs, architecture docs
- Identify the core modules and their responsibilities
- Assess module boundaries, coupling, cohesion
- Look for god objects (classes with too many responsibilities)
- Check for circular dependencies
- Evaluate the build/bundle pipeline

**Agent 2 — Code Quality & Bugs:**
- Read the largest/most critical source files thoroughly
- Look for actual bugs: off-by-one errors, uninitialized variables, race conditions, edge cases
- Check error handling: swallowed errors, inconsistent patterns, raw exceptions shown to users
- Look for dead code, unused imports, unreachable branches
- Check naming consistency, coding style consistency
- Look for magic numbers, hardcoded values that should be configurable
- Identify code duplication (copy-pasted blocks, near-identical functions)
- Check for proper resource cleanup (file handles, connections, temp files)

**Agent 3 — Security & Licensing:**
- Search for ALL shell execution patterns (system, exec, backticks, eval, spawn, child_process, subprocess, os.system, etc.)
- Search for ALL file operations and check for path traversal, symlink attacks, TOCTOU races
- Check for injection vulnerabilities (SQL, command, XSS, template, regex)
- Check for hardcoded secrets, credentials, API keys
- Look for unsafe deserialization, prototype pollution, or equivalent language-specific risks
- Check for predictable random values used for security purposes
- Read LICENSE files, check for attribution requirements
- Search for copied/vendored code without attribution
- Check dependency licenses for compatibility

**Agent 4 — Tests & Documentation:**
- Read ALL test files — assess coverage breadth and depth
- Identify tautological tests (tests that pass even when code is broken)
- Look for tests that verify messages/strings instead of actual behavior
- Check for flaky tests (timing-dependent, order-dependent, environment-dependent)
- Identify major untested code paths
- Read ALL documentation files
- Cross-reference docs against actual code — find stale claims, wrong references
- Check for contradictions between different docs
- Verify that documented features actually exist in code
- Check if claimed metrics (coverage %, performance numbers) are substantiated

**Agent 5 — Performance & Duplication:**
- Identify hot paths (rendering loops, request handlers, per-frame/per-request code)
- Look for O(n^2) or worse algorithms in hot paths
- Check for unnecessary work (recomputation, redundant I/O, missing caches)
- Look for string concatenation in loops (language-dependent: bad in Java/Perl/Python, fine in others)
- Check for N+1 query patterns, unbatched operations
- Look for missing debouncing, throttling, or pagination
- Catalog all duplicated code patterns with specific locations
- Identify abstractions that should exist but don't

**Agent 6 — Agent Readiness:**
- Read the agent-facing instructions (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`) and check **every factual claim** against the code — stale rules are the finding, not the absence of rules
- Find the work queue. Is it ranked? Are there duplicate or dangling entry numbers? Are the owner's own requests distinguishable from machine-generated ones?
- Find the verification recipe. Run it. Does it work *right now*? How many environments does it cover?
- Hunt vacuous gates: for every test threshold and CI check, ask what input would make it fail. Report each one that has no answer
- Look for thresholds set just above a measured failure rate, tests whose names promise more than their assertions deliver, and tests loosened to accommodate a bug
- Check isolation: worktrees, ports, shared machine-wide singletons (devices, session pools, databases, keychains), whether production is guard-blocked, and whether real credentials or personal data are reachable from an ordinary task
- Check whether lessons are recorded anywhere, and whether the same mistake recurs in the history

### Phase 1.5: External Security Cross-Check (best-effort)

Alongside Agent 3, attempt an independent second opinion from a different model via the `delegate-security-audit` skill. This exists because a single model — including Claude auditing its own analysis — misses classes of vulnerabilities another model catches, and Claude's own guardrails limit how adversarially it will probe certain code. Treat this as strictly additive: if it's unavailable, the scorecard proceeds on Agent 3 alone.

**Check availability first; skip silently if unavailable:**

```bash
command -v pi >/dev/null && pi auth check --provider openrouter --no-refresh >/dev/null 2>&1 && echo available
```

If `pi` isn't installed, or the OpenRouter credential check fails, don't attempt the delegation — proceed with Agent 3's findings alone and note in the report: "External security cross-check skipped (delegate-security-audit unavailable: `pi` not installed / OpenRouter not authenticated)." Never block or fail the scorecard over this being unavailable.

**If available**, invoke the `delegate-security-audit` skill (via the Skill tool) for guidance, but override its default behavior for this context: **scorecard is a read-only grading tool**, so brief GLM explicitly not to modify any files, and run its `pi` command with `--exclude-tools edit,write` appended (the same read-only pattern `delegate-review` uses) regardless of what that skill's own example shows — a grading pass must never leave code changes behind as a side effect. Give it the same scope Agent 3 covers (shell execution patterns, path traversal/symlink/TOCTOU, injection, hardcoded secrets, unsafe deserialization, predictable randomness in security contexts) and ask for a report — findings with file:line and severity, not fixes. Run it in the background (`run_in_background`) while the other Phase 1 agents work, since it can take several minutes; this costs real money, which is expected for a periodic scorecard run per CLAUDE.md, but don't loop it.

Fold its findings into Agent 3's before grading, tagging each with its source. Where the two disagree on severity, or one surfaces something the other missed, note the discrepancy in the report rather than silently picking one — the disagreement itself is signal.

### Phase 2: Grading

After all agents complete, synthesize findings into grades. Be honest and critical. A "B" should mean genuinely good code, not "I didn't look hard enough to find problems."

## Evaluation Dimensions

### 1. Architecture (Weight: High)
How well-structured is the codebase? Are responsibilities clear?
- **A**: Clean separation of concerns, clear module boundaries, dependency injection, single responsibility
- **B**: Good structure with minor coupling issues or one area of unclear responsibility
- **C**: Some modules doing too much, moderate coupling, unclear boundaries in places
- **D**: God objects, circular dependencies, tangled responsibilities
- **F**: Monolithic, no discernible structure

### 2. Code Quality (Weight: High)
Is the code correct, readable, and maintainable?
- **A**: No bugs found, clear naming, good error handling, proper resource cleanup throughout
- **B**: Minor issues, readable, mostly correct
- **C**: Some bugs or error handling gaps, readability issues in places
- **D**: Multiple bugs, poor readability, missing error handling
- **F**: Pervasive bugs, unreadable code

### 3. Consistency (Weight: Medium)
Are patterns, naming, and conventions uniform across the codebase?
- **A**: Uniform patterns, naming, error handling, and style throughout
- **B**: Mostly consistent with minor variations
- **C**: Inconsistent in some areas — different patterns for the same problem
- **D**: Wildly different styles across files, no discernible conventions
- **F**: Every file looks like it was written by a different person

### 4. Security (Weight: High)
Are there vulnerabilities? Is the threat model appropriate? Grade from the combined findings of Agent 3 and the external cross-check (Phase 1.5), when the latter ran — tag each finding with its source (`[Agent 3]` / `[GLM]`) in the Critical Issues list.
- **A**: No vulnerabilities found, proper input validation, secure defaults, documented threat model
- **B**: Minor gaps but no exploitable issues, good practices overall
- **C**: Some risks that need attention (e.g., unsanitized input in non-critical paths)
- **D**: Exploitable vulnerabilities present
- **F**: Critical vulnerabilities (injection, auth bypass, data exposure)

### 5. Performance (Weight: Medium)
Is the code efficient where it matters?
- **A**: Hot paths are optimized, appropriate caching, no unnecessary work
- **B**: Generally efficient, minor optimization opportunities
- **C**: Some unnecessary work in hot paths, missing obvious caches
- **D**: O(n^2) in hot paths, redundant I/O, no caching where needed
- **F**: Fundamentally broken performance characteristics

### 6. DRY / Duplication (Weight: Medium)
Is logic expressed once, or copy-pasted?
- **A**: No meaningful duplication, good abstractions at the right level
- **B**: Minor duplication, mostly DRY
- **C**: Noticeable copy-paste that should be refactored (3+ instances)
- **D**: Significant duplication across files
- **F**: Rampant copy-paste throughout

### 7. Testability (Weight: Medium)
Is the code designed to be testable?
- **A**: Dependency injection, clear interfaces, pure functions, easy to mock boundaries
- **B**: Mostly testable, minor coupling issues
- **C**: Some components hard to test in isolation, tight coupling in places
- **D**: Tightly coupled, requires complex setup to test anything
- **F**: Untestable — global state, hidden dependencies, no seams

### 8. Test Coverage & Quality (Weight: Medium)
Do tests exist, and do they actually catch bugs?
- **A**: Comprehensive coverage, tests verify behavior (not just smoke tests), edge cases covered
- **B**: Good coverage with minor gaps, tests are meaningful
- **C**: Tests exist but have gaps, some tautological tests, missing edge cases
- **D**: Sparse tests, many tautological, major features untested
- **F**: No tests or tests that always pass

### 9. Type Safety (Weight: Medium)
Is the type system used effectively? (Grade within the language's capabilities — don't penalize Perl for not being TypeScript.)
- **A**: Strong typing throughout, generics used well, no escape hatches
- **B**: Good typing with minor gaps (a few `any`/`Object`/untyped areas)
- **C**: Mixed — some typed, some untyped, type assertions used as shortcuts
- **D**: Weak typing, frequent escape hatches, types are lies
- **F**: No typing, or types are so wrong they're misleading
- **N/A**: Language has no type system (Python without hints, Perl, shell scripts) — skip this dimension and redistribute weight

### 10. Documentation (Weight: Medium)
Is the project documented? Are docs accurate?
- **A**: Comprehensive, accurate, up-to-date docs; code is self-documenting where appropriate
- **B**: Good docs with minor gaps or slightly stale references
- **C**: Docs exist but have inaccuracies, stale references, or significant gaps
- **D**: Minimal or mostly wrong documentation
- **F**: No documentation, or docs that actively mislead

### 11. Error Handling (Weight: Medium)
Does the code handle failures gracefully?
- **A**: Comprehensive error handling, typed errors, graceful degradation, clear user messages
- **B**: Good coverage, minor gaps, consistent patterns
- **C**: Basic handling, some swallowed errors or inconsistent patterns
- **D**: Many unhandled cases, errors swallowed or leak implementation details
- **F**: No error handling, crashes on unexpected input

### 12. Extensibility (Weight: Low)
How easy is it to add features or modify behavior?
- **A**: Plugin architecture or clear extension points, open/closed principle
- **B**: Reasonably extensible, adding features is straightforward
- **C**: Can be extended but requires modifications to existing code
- **D**: Hard to extend without significant refactoring
- **F**: Requires rewrite to add features

### 13. Repo Hygiene (Weight: Low)
Is the repository clean, well-organized, and professional?
- **A**: Clean git history, proper .gitignore, no junk files, CI configured, clear branching strategy
- **B**: Mostly clean with minor issues
- **C**: Some junk files, messy history, incomplete .gitignore
- **D**: Significant clutter, broken CI, no .gitignore
- **F**: Repository is a mess

### 14. Accretion (Weight: Medium)
Is the codebase being folded back as it grows, or only added to? This is a *trend* — the other thirteen grade the tree as it stands; this grades its direction. Run `/slop --quick` and report its grade; that skill owns the method (articulability and surface area decide; history is evidence; smells only annotate). DRY (#6) measures duplication *present*; this measures whether duplication and size are being *removed*. Fix commits that delete nothing, fix-of-a-fix chains in one file, a refactor share near zero, and a tracker that only grows are the signals.
- **A**: Surface area flat or shrinking over the window; refactoring visibly happening; fixes name causes and delete something
- **B**: Mostly chosen; occasional additive fix or unexplained growth
- **C**: Accreting — production add:delete climbing, refactor share near zero, god files growing
- **D**: Sediment — fix-of-a-fix chains, nobody can say why half of it is there
- **F**: Dead in Naur's sense: modifiable, but not well

---

## Agent-Readiness Dimensions

A second, separate table. The 13 dimensions above grade the code. These grade whether **an agent could work here unattended for eight hours without a human** — a different question, and increasingly the one that determines throughput.

Grade these even on a project that has never been worked on by agents; the answer tells the owner what it would cost to start. Skip the whole table only if the user asks for `--quick`.

### A1. Tracking & Priorities (Weight: High)
Is there a work queue an agent can read, rank, and update without guessing?
- **A**: Tracker exists and is prioritised; the human's own direct requests are tracked *separately* and ranked above machine-found work; no duplicate or dangling entry numbers; stale entries pruned
- **B**: Good tracker, minor staleness, human requests not separated but not being buried either
- **C**: Tracker exists but is unranked or has grown past the point of being readable; human requests compete on equal footing with machine-generated items
- **D**: Inline `TODO:` comments only, or a tracker nobody updates
- **F**: No queue — an agent has nothing to pull from

*Check for:* duplicate heading numbers, references pointing at renumbered or deleted entries, entries marked done that aren't, and whether anything distinguishes "the owner asked for this" from "an agent found this."

### A2. Verifiability (Weight: High)
Can an agent confirm a change works, by driving the real thing?
- **A**: A documented recipe for exercising the product end to end (drive the UI, run the binary, curl the endpoint), it works right now, and it covers more than one environment
- **B**: Recipe exists and works, single environment
- **C**: Tests only — nothing that exercises the assembled product; an agent must infer that a feature works from unit coverage
- **D**: Tests are slow, manual, or partly broken; no path from "code changed" to "product works"
- **F**: No way to verify anything without a human

*This is the highest-leverage dimension.* Without it, everything merges on the strength of reports.

*Check for:* a harness that only ever runs in one configuration (one origin, one screen size, one locale) — that makes an entire class of bug structurally invisible. And **can the fixtures exhibit the properties their tests assert?** A corpus that alternates authors so a multi-revision session is unreachable by construction, two rounds with byte-identical images so "image changed" can never fire, a field the real API never returns — construct the failing case by hand and confirm the fixture could produce it.

### A3. Guard Integrity (Weight: High)
Do the project's own checks actually fail when something is wrong?
- **A**: Gates are meaningful and proven; thresholds derived from requirements; CI enforces architectural invariants, not just lint
- **B**: Solid gates, one or two soft thresholds
- **C**: Some gates cannot fail as written, or thresholds are set just above a measured failure rate — enshrining the failure rather than fixing it
- **D**: Tests pass when the code is broken; assertions check log messages rather than behaviour
- **F**: Green means nothing

*Actively hunt vacuous gates.* For each one ask: **what input would make this fail?** Report every gate with no answer. Also flag tests whose names promise more than their assertions deliver, and any test loosened to accommodate a known bug.

*Check for:* **a verdict-file mechanism** — does the check tool write instrument exit codes and the HEAD it ran at somewhere a merge path can read *instead of the worker's report*? Workers have reported "clean build" over a machine-readable refusal; a project whose only record of a check is the agent's say-so cannot grade above C here. And **every predicate ships with the case that must not trigger it** — a rule tested only on the input its author wrote is unproven.

### A4. Isolation & Safety (Weight: High)
Can several agents work at once without corrupting each other or the owner's real data?
- **A**: Worktree-per-agent is the norm; machine-wide shared singletons (devices, session pools, ports, databases, keychains) are documented with collision-avoidance; production is explicitly guard-blocked; credentials and personal data never enter agent context
- **B**: Good isolation, shared resources undocumented but not currently colliding
- **C**: Agents share a checkout or a device; collisions happen and get misdiagnosed as product bugs
- **D**: No isolation; real credentials or personal data reachable from a normal task
- **F**: An agent can destroy the owner's production data by following instructions

*Security-style rule: if agents can reach production data or credentials, this cannot be graded above C.*

*Check for:* **tripwires on global-blast-radius files** — are the few places where any change has global effect (default configs, prompts, ranking loops, abstention gates, the production asset) guarded by a test that fails on content change without an explicit marker? An escalation instruction without one is a wish. And **reversible destructive tooling** — do the project's own reapers, purgers and cleanup scripts quarantine rather than delete, take a required root with no default, and read a liveness signal themselves? A reaper once deleted two live agents' worktrees; a purge script came one guard line from `rm -rf /*`.

### A5. Knowledge Capture (Weight: Medium)
Does the project remember what it learned, and does the learning escape the project?
- **A**: Lessons recorded with cost and cause; generalisable ones promoted into shared tooling; existing lessons sharpened rather than duplicated; instructions to agents match what the code actually does
- **B**: Good diary or lessons file, slightly behind
- **C**: Lessons live only in commit messages and issue threads; the same mistake is re-learned
- **D**: Agent instructions (`CLAUDE.md` and similar) contradict the code — **stale rules are worse than none**, because they are trusted
- **F**: Nothing recorded

*Check every factual claim in the agent-facing instructions against the code.* A rule stated as absolute with an undocumented exception is a finding: readers trust it and audit against it.

---

## Output Format for Agent-Readiness

```
| #  | Dimension            | Grade | Key Finding |
|----|----------------------|-------|-------------|
| A1 | Tracking & Priorities| C     | 134 entries, 3 references point at a renumbered item |
| A2 | Verifiability        | B+    | Real device harness; only ever driven from one origin |
| A3 | Guard Integrity      | C-    | A documented gate does not exist in code; one suite cannot fail |
| A4 | Isolation & Safety   | B     | Worktrees used; shared device collisions misread as page bugs |
| A5 | Knowledge Capture    | B-    | Excellent lessons in code comments, not propagated to docs |

**Agent-Readiness: C+**
```

Then, in the detailed report, add one section: **"What would break first in an unattended run"** — the single change that would most increase how long agents can work here without a human. Be concrete and name the file.

## Output Format

### Summary Scorecard

```
# Codebase Scorecard: [Project Name]

**Audited**: [date] | **Size**: [X files, Y KLOC] | **Language(s)**: [primary languages]

| # | Category          | Grade | Key Finding |
|---|-------------------|-------|-------------|
| 1 | Architecture      | B+    | Clean renderer; Editor is a god object |
| 2 | Code Quality      | B-    | Good conventions documented, inconsistently followed |
| 3 | Consistency       | B     | Mostly uniform, some mixed patterns |
| 4 | Security          | C-    | Multiple shell injection vectors |
| 5 | Performance       | C     | Uncached hot-path computation |
| 6 | DRY               | C+    | 5+ duplicated patterns identified |
| 7 | Testability       | B+    | Pure renderer, DI in most modules |
| 8 | Test Coverage     | B-    | Good breadth, tautological in places |
| 9 | Type Safety       | N/A   | Perl — no type system |
| 10| Documentation     | C     | Multiple stale references |
| 11| Error Handling    | C+    | Inconsistent user-facing messages |
| 12| Extensibility     | B     | Good plugin points, tight core coupling |
| 13| Repo Hygiene      | B-    | Junk files, missing .gitignore entries |
| 14| Accretion         | C     | Add:delete 7:1 in production code; zero refactor moves in 110 commits |

**Overall: C+**
```

### Detailed Report

After the summary table, provide these sections:

#### Top Strengths (3-5 bullets)
What the project does well. Be specific — cite files and patterns.

#### Critical Issues (prioritized list)
Issues that should block a release or be fixed immediately. Include:
- Severity (CRITICAL / HIGH / MEDIUM / LOW)
- Category tag (e.g., [Security], [Bug], [Performance])
- Specific file:line references
- Brief description of the issue and its impact
- Suggested fix

#### Architecture Assessment (2-3 paragraphs)
Honest assessment of the overall design. What's the biggest structural problem? What design decision will cause the most pain as the project grows?

#### Documentation vs Reality
List every place where documentation contradicts the actual code. Be specific with quotes from docs and what the code actually does.

#### Quick Wins (3-5 items)
Easy fixes that would meaningfully improve quality. Each should be achievable in a single commit.

#### Technical Debt (if applicable)
Larger structural issues that need sustained effort. For each item, describe the current state, the target state, and a rough sense of scope (single file vs cross-cutting).

## Grading Scale

| Grade | Meaning | Implication |
|-------|---------|-------------|
| A+/A  | Excellent | Ship with confidence |
| A-/B+ | Very good | Minor polish needed |
| B/B-  | Solid | Some issues to address |
| C+/C  | Fair | Needs attention before scaling |
| C-/D+ | Below average | Significant work needed |
| D/D-  | Poor | Major problems |
| F     | Failing | Fundamental issues |

**Overall grade** = weighted average, but drag it down if any HIGH-weight category is D or below. A project with A architecture but F security is not a B — it's a C at best.

## Worked Example

```
# Codebase Scorecard: payment-service

**Audited**: 2026-03-06 | **Size**: 42 files, 8.2 KLOC | **Language(s)**: TypeScript

| # | Category          | Grade | Key Finding |
|---|-------------------|-------|-------------|
| 1 | Architecture      | A-    | Clean adapter pattern, single responsibility |
| 2 | Code Quality      | B+    | One off-by-one in retry logic |
| 3 | Consistency       | A     | Uniform error handling and naming throughout |
| 4 | Security          | A     | Input sanitized, no secrets in code |
| 5 | Performance       | B     | Minor: unbatched DB reads in reconciliation |
| 6 | DRY               | B     | Validation logic duplicated in 2 handlers |
| 7 | Testability       | A     | DI throughout, pure business logic functions |
| 8 | Test Coverage     | B     | 80% coverage, needs E2E for webhook flow |
| 9 | Type Safety       | A     | Full TypeScript strict, no `any`, proper generics |
| 10| Documentation     | B-    | Missing JSDoc on PaymentProcessor class |
| 11| Error Handling    | B+    | Good custom error classes, add retry for transient |
| 12| Extensibility     | A     | Easy to add new payment providers via adapter |
| 13| Repo Hygiene      | A-    | Clean history, CI configured, one stale branch |

**Overall: B+**

### Top Strengths
- Adapter pattern in `src/providers/` makes adding payment providers trivial — add one file, register in factory
- Custom error hierarchy (`PaymentError` → `ValidationError` | `ProviderError` | `TimeoutError`) with proper propagation
- Comprehensive TypeScript strict mode, zero `any` usages, well-typed generics on `Result<T, E>`

### Critical Issues
- **MEDIUM [Bug]** `src/retry.ts:45` — off-by-one in exponential backoff: `delay = baseDelay * (2 ** attempt)` should be `2 ** (attempt - 1)` since `attempt` is 1-indexed. First retry waits 2x too long.
- **MEDIUM [Performance]** `src/reconciliation.ts:112-130` — reconciliation handler loads transactions one-by-one in a loop instead of batching. Will hit N+1 at scale.

### Architecture Assessment
Clean layered architecture. The provider adapter pattern (`src/providers/base.ts` → Stripe, PayPal, etc.) is well-designed and follows open/closed principle. Business logic is properly separated from I/O in `src/domain/`.

The one concern is that `src/handlers/webhook.ts` (340 lines) is doing too much — parsing, validation, idempotency checking, event dispatching, and error recovery. This should be split into a webhook parser and an event dispatcher.

### Quick Wins
1. Extract `src/validation.ts:45-89` shared logic from `src/handlers/charge.ts:23-67` — removes duplication, DRY grade → A-
2. Add JSDoc to `PaymentProcessor` and `ProviderFactory` public methods — Documentation grade → B+
3. Fix retry off-by-one — Code Quality grade → A-
```

## Guidelines for the Auditor

- **Be genuinely critical.** A useful audit finds real problems. Praising everything helps nobody.
- **Read actual code.** Don't grade based on file names or README claims. Verify.
- **Cite specific evidence.** Every grade must reference concrete findings with file:line.
- **Don't penalize for language limitations.** Perl doesn't have type safety — don't dock points for that. Grade within the language's idioms.
- **Don't penalize for scope.** A small project doesn't need a plugin architecture. Grade proportionally.
- **Do penalize for claims vs reality.** If docs claim "95% test coverage" but there are no metrics, that's a documentation problem.
- **Security issues are never "low priority."** If you find an exploitable vulnerability, the Security grade cannot be above C regardless of how good everything else is.
- **Consider the codebase's stage.** An MVP doesn't need the same polish as a mature production system. Grade proportionally to ambition and maturity — but still flag real risks regardless of stage.
- **Check the junk drawer.** Look at git status, untracked files, temp files, debug artifacts. These reveal working habits.
