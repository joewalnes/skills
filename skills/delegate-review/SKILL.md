---
name: delegate-review
description: Get an independent second-opinion code review of Claude's own work from a different model lineage (Kimi K3, or GPT 5.6 Sol as alternate) via pi. Use when the user wants Claude's work checked by another AI, not just self-reviewed.
argument-hint: <what to review>
---

# Delegate: independent second opinion (review)

A reviewer from a different model lineage checks work you (Claude) produced. Default Kimi K3; `openai/gpt-5.6-sol` is the alternate (note: it reserves 128k output tokens per request, which can trip OpenRouter's 402 "requires more credits" daily-limit error if the account's daily key limit is low — if that happens, use Kimi or ask the user to raise the key's daily limit).

**Zero data retention (ZDR):** the user's OpenRouter account rejects non-ZDR endpoints. Don't suggest loosening this policy to work around a model that 404s.

```bash
cd <repo-root> && pi -p --provider openrouter --model moonshotai/kimi-k3 \
  --thinking high --exclude-tools edit,write --session-id delegate-review "<brief>"
```

- `--exclude-tools edit,write` keeps the reviewer read-only — it inspects, you decide what to apply.
- Brief it with what changed and how to see it, e.g.: "You are an independent code reviewer. Review the uncommitted changes (git diff HEAD) in this repo, which implement X. Look for bugs, design problems, and missed edge cases. Be critical; don't rubber-stamp. Report findings with file:line."
- Relay its findings honestly, including criticism of your own work, then give your own take on each finding — agree, rebut with reasons, or fix.

## Continuity

Always pass `--session-id delegate-review`. Follow-up delegations continue with full memory of prior exchanges. Use a new id (`delegate-review-2`) to start fresh.
