#!/usr/bin/env python3
"""Rebuild an unpushed range of commits into fewer, cleaner, atomic ones — by theme, in order.

  consolidate.py [--repo R] [<base>..<head>]        propose groups (default range: @{upstream}..HEAD)
  consolidate.py [--repo R] [<base>..<head>] --apply [--messages FILE]   (FILE: JSON list, one per group;
                                                                          or {"<group#>": "msg"} overrides)

Groups are CONTIGUOUS runs of commits that share a theme (a "prefix:" subject, or
heavily overlapping files). Contiguous-only means the rebuild is always safe: each
group's end tree is exactly the original history's tree at that point, so no
reordering, no conflicts. The result is verified byte-identical to the old tip.
Refuses on a dirty tree, and on any commit already reachable from the upstream.
A backup tag (backup/consolidate-<ts>) points at the old tip.
"""
import argparse, json, re, subprocess, sys
from datetime import datetime

def git(repo, *a, check=True):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=check).stdout

PREFIX = re.compile(r"^([a-z][\w./-]{1,30}):\s", re.I)
FIXY = re.compile(r"^(fix|fixup|wip|oops|typo|revert|address review|tweak|cleanup|lint|fmt|format)\b", re.I)

def commits(repo, rng):
    out = git(repo, "log", "--reverse", "--format=%H%x1f%s%x1f%b%x1e", rng)
    rows = []
    for rec in out.split("\x1e"):
        if not rec.strip(): continue
        h, subj, body = (rec.strip("\n").split("\x1f") + ["", ""])[:3]
        files = set(git(repo, "show", "--format=", "--name-only", h).split())
        rows.append({"hash": h, "subject": subj, "body": body.strip(), "files": files})
    return rows

def theme(c):
    m = PREFIX.match(c["subject"])
    return m.group(1).lower() if m else None

def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0

def propose(rows):
    groups = []
    for c in rows:
        if groups:
            g = groups[-1]; last = g[-1]
            same_prefix = theme(c) and theme(c) == theme(last)
            fixup = FIXY.match(c["subject"]) and jaccard(c["files"], set().union(*(x["files"] for x in g))) > 0
            overlap = jaccard(c["files"], set().union(*(x["files"] for x in g))) >= 0.5
            if same_prefix or fixup or overlap:
                g.append(c); continue
        groups.append([c])
    return groups

def default_message(g):
    if len(g) == 1:
        return g[0]["subject"] + ("\n\n" + g[0]["body"] if g[0]["body"] else "")
    t = theme(g[0])
    title = f"{t}: {len(g)} changes consolidated" if t else g[0]["subject"]
    lines = [title, "", f"Consolidated from {len(g)} commits:"] + [f"- {c['subject']}" for c in g]
    trailer = next((l for c in g for l in c["body"].splitlines() if l.startswith("Co-Authored-By:")), None)
    if trailer: lines += ["", trailer]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("range", nargs="?"); ap.add_argument("--repo", default=".")
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--messages", help="JSON list of commit messages, one per group (default: generated)")
    a = ap.parse_args(); repo = a.repo
    if git(repo, "status", "--porcelain").strip():
        sys.exit("refusing: working tree is not clean")
    rng = a.range or "@{upstream}..HEAD"
    base, _, head = rng.partition(".."); head = head or "HEAD"
    base_sha = git(repo, "rev-parse", base).strip(); head_sha = git(repo, "rev-parse", head).strip()
    up = git(repo, "rev-parse", "@{upstream}", check=False).strip()
    if up and subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", head_sha, up], capture_output=True).returncode == 0:
        sys.exit("refusing: this range is already pushed")
    rows = commits(repo, f"{base_sha}..{head_sha}")
    if not rows: sys.exit("nothing to consolidate")
    groups = propose(rows)
    print(f"{len(rows)} commits -> {len(groups)} groups\n")
    for i, g in enumerate(groups, 1):
        print(f"[{i}] {default_message(g).splitlines()[0]}")
        if len(g) > 1:
            for c in g: print(f"      {c['hash'][:8]}  {c['subject'][:80]}")
    if not a.apply:
        print("\n(dry run — pass --apply to rebuild; --messages FILE to supply your own messages)"); return
    msgs = [default_message(g) for g in groups]
    if a.messages:
        spec = json.load(open(a.messages))
        if isinstance(spec, dict):                 # {"1": "msg", "3": "msg"} — override only these groups (1-based)
            for k, v in spec.items(): msgs[int(k) - 1] = v
        else:
            assert len(spec) == len(groups), "one message per group"; msgs = spec
    tag = f"backup/consolidate-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    git(repo, "tag", tag, head_sha)
    git(repo, "reset", "-q", "--hard", base_sha)
    for g, msg in zip(groups, msgs):
        end = g[-1]["hash"]
        git(repo, "read-tree", "-u", "--reset", end)      # index + worktree := that commit's tree, deletions included
        git(repo, "commit", "-q", "--allow-empty", "-m", msg)
    if git(repo, "diff", "--stat", tag).strip():
        sys.exit(f"VERIFY FAILED: tree differs from {tag}; history left as rebuilt, backup tag kept")
    print(f"\nrebuilt {len(rows)} -> {len(groups)} commits; tree identical to {tag}")
    print(git(repo, "log", "--oneline", f"{base_sha}..HEAD"))
    print(f"backup: {tag}  (git tag -d {tag} once pushed)")

if __name__ == "__main__":
    main()
