---
name: consolidate
description: Rebuild unpushed commits into fewer clean atomic ones by theme, tree verified identical. Use before pushing, or in go-team's gate before merging a worker branch.
argument-hint: [<base>..<head>] [--apply]
---

# Consolidate: commit often, push clean

Frequent commits are right while working — they're checkpoints, and `commit as you go` is a go-team rule for good reason. But a history of `fix`, `fix the fix`, `docsite: a`, `docsite: b`, `oops` is a cost every future reader pays, and the fleets' logs had become exactly that. So: commit as often as you like on a branch, and **before a push — or, in go-team, before a worker branch merges — rebuild the range into commits a reader would choose.**

Still atomic. One logical change per commit is the repo rule; consolidation makes commits *match* that rule, not violate it. A group is a theme, not "everything since Tuesday."

## Running it

```bash
python3 ~/.claude/skills/consolidate/scripts/consolidate.py                 # propose, on @{upstream}..HEAD
python3 ~/.claude/skills/consolidate/scripts/consolidate.py main..HEAD      # propose, explicit range
python3 ~/.claude/skills/consolidate/scripts/consolidate.py --apply         # rebuild
python3 ~/.claude/skills/consolidate/scripts/consolidate.py --apply --messages msgs.json
```

Propose first. Read the groups. If the grouping is right but the generated messages aren't, write a JSON list of messages (one per group, in order) and pass `--messages` — a consolidated message should say what the change *is*, not list what was squashed; the script's default lists the squashed subjects as a fallback, which is honest but not good.

## How it groups, and why that's safe

Groups are **contiguous runs** of commits sharing a theme: the same `prefix:` in the subject, a fixup-shaped subject (`fix`, `wip`, `typo`, `revert`, `lint`…) touching files the run already touched, or heavy file overlap. Contiguous-only is deliberate: each group's end tree is exactly the original history's tree at that point, so the rebuild is a sequence of `read-tree` + `commit` with no reordering and no possibility of conflict. It won't gather two related commits that have an unrelated one between them — accept that, or reorder by hand first. The result is verified byte-identical to the old tip; a backup tag points at the old history until you delete it.

It refuses on a dirty tree and on a range already reachable from the upstream. Never consolidate what others have pulled.

## Where it runs

- **You, before `git push`.** The dev-loop rule: commit often, consolidate before push.
- **go-team's gate**, before `git merge --no-ff` of a worker branch: run it on `main..<branch>` and apply, so a worker's twelve checkpoints land as the two or three changes they were. The `Thesis:` and `Surface:` trailers survive in the consolidated message (the first body carrying them is kept). See `references/gate.md`.
- **Not on `main` after merges.** Merge commits are already the unit there.

## What it does not do

It doesn't rewrite messages intelligently — that's judgement, yours or the foreman's, via `--messages`. It doesn't reorder. It doesn't touch pushed history. If a range has genuinely thirty distinct changes, it will propose thirty groups, and that's the right answer.
