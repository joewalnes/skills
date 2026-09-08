# go-team — Fleet tooling is code too

Part of the `/go-team` skill; read before writing or running any tooling that deletes or moves things. The loop itself is in `SKILL.md`.

## Long commands: the form workers are handed

Paste this into any brief whose work includes a command that can outlive a tool call's foreground timeout (builds, simulator batches, fuzzers, full evals). Start detached, then wait in a **bounded** loop inside **one** tool call with an explicit timeout under the tool's cap; never end a turn waiting for a notification.

```sh
LOG="$SCRATCH/run-$(git rev-parse HEAD)-$$.log"            # unique per run, never a fixed path
nohup <long command> > "$LOG" 2>&1 & echo $! > "$LOG.pid"
```
```sh
# a later tool call, timeout set to e.g. 540000 ms (under the 600000 cap); repeat the call if it times out
for i in $(seq 1 50); do kill -0 "$(cat "$LOG.pid")" 2>/dev/null || break; sleep 10; done
kill -0 "$(cat "$LOG.pid")" 2>/dev/null && echo STILL-RUNNING || { echo DONE; tail -20 "$LOG"; }
```

If the harness offers a `Monitor` tool, use it instead of the loop; the shape is the same — a bounded wait you own, inside the turn.

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

