---
name: delegate
description: Delegate a task to an external non-Claude agent — image generation (OpenRouter image models), deep security analysis (GLM via pi), private on-device work (local Ollama via pi), second-opinion code review (Kimi/GPT via pi), or cheap bulk grunt work. Use when the user asks to generate a logo/image/photo, run a security audit, process data that must never leave the device, get an independent review of Claude's work, or churn through high-volume simple tasks.
argument-hint: <image|sec|private|review|bulk> <task>
---

# Delegate to external agents

Route a task to one of the external agents below, wait for the result, and report back. These are real independent agents — treat them like subagents you brief, not APIs you call. Give each one a complete, self-contained brief: the task, the relevant paths, and what form the output should take.

All agents run through tools already on this machine: `pi` (CLI coding agent) and Ollama. Cloud models go through the user's OpenRouter account; `pi` holds the key — never ask for or echo API keys.

**Zero data retention (ZDR):** the user's OpenRouter account is configured to reject routing to any non-ZDR endpoint. A 404 "No endpoints available matching your … data policy" means the model has no ZDR endpoint — that rejection is deliberate. Never suggest loosening the account setting to make a model work; pick a different model instead. If the user explicitly wants a specific non-ZDR model anyway, state clearly that it is not zero-retention and get their confirmation before they change anything.

## Agent roster

| Agent | Backend | Use for |
|---|---|---|
| `image` | OpenRouter image models via `scripts/generate-image.py` | Logos, photorealistic images, product shots, image editing |
| `sec` | GLM 5.3 via `pi` + OpenRouter | Deep security analysis: finding and fixing vulnerabilities in the user's own codebases |
| `private` | qwen3.6:35b-mlx via `pi` + local Ollama | Anything touching data that must never leave this device (personal notes, PII, confidential docs) |
| `review` | Kimi K3 (or GPT 5.6 Sol) via `pi` + OpenRouter | Independent second-opinion review of work Claude has done, from a different model lineage |
| `bulk` | Gemini 2.5 Flash Lite (near-free) via `pi` + OpenRouter | High-volume, low-intelligence grunt work: mass content review, generating test/sample data, mechanical transforms. Non-private data only |

If the user names a task that fits one of these, suggest delegating even if they didn't say `/delegate`.

## Continuity (sessions)

`pi` agents keep persistent per-project sessions. Always pass `--session-id delegate-<agent>` (e.g. `delegate-sec`). The first call warns "creating a new session" — that's normal. Follow-up delegations to the same agent automatically continue with full memory of prior exchanges, so you can brief incrementally like you would a colleague. To start fresh, use a new id (`delegate-sec-2`).

## `image` — image generation

```bash
python3 <skill-dir>/scripts/generate-image.py "<detailed prompt>" -o <name>.png
```

- Default model is `google/gemini-3-pro-image` (best quality that passes the ZDR policy). For quick drafts or iterations add `-m google/gemini-3.1-flash-lite-image` (fast/cheap). OpenAI image models (`openai/gpt-5.4-image-2` etc.) have no ZDR endpoints and are rejected by the account — see ZDR note above.
- To edit or reference an existing image (e.g. "this person wearing a red jacket"), pass `-i input.png` (repeatable).
- Write the prompt yourself, expanded from the user's ask: subject, style, composition, background, lighting. Don't just forward their words verbatim.
- Save into the project or scratchpad as appropriate, then send the result with SendUserFile (`display: render`) so the user sees it immediately — they're often on mobile.
- Generation takes 30–120s; use a generous Bash timeout.

## `sec` — security analysis (GLM 5.3)

For authorized security work on the user's own code: audits, vulnerability hunting, and fixing what's found.

```bash
cd <repo-root> && pi -p --provider openrouter --model z-ai/glm-5.3 \
  --thinking high --session-id delegate-sec "<brief>"
```

- This is a full coding agent with read/bash/edit/write tools in the repo — it can apply fixes, not just report.
- Brief it with scope and deliverable, e.g.: "Audit the auth and session-handling code in src/ for vulnerabilities (injection, authz bypass, secrets handling, SSRF). Fix what you find, and summarize each issue, severity, and fix."
- Long audits can run many minutes: use `run_in_background` and report when it finishes.
- Afterward, run `git diff` and review its changes yourself before presenting them — you own the final quality bar.

## `private` — on-device only (local qwen3.6)

For tasks over data the user never wants leaving the device. The model runs locally via Ollama (127.0.0.1); `--offline --no-extensions` keeps pi itself from any network calls.

```bash
pi -p --offline --no-extensions --provider ollama --model qwen3.6:35b-mlx \
  --session-id delegate-private "<brief>"
```

**Privacy protocol — this is the entire point of this agent:**

1. **Never read the private material yourself** — no Read, cat, grep, head on it. Anything that enters your context leaves the device. Refer to it by path only.
2. Brief the local agent with paths, not content: "Read ~/notes/medical.md and summarize action items into ~/notes/medical-summary.md."
3. **Tell it to write output to a file and reply with only the file path and a one-line non-sensitive status.** Its stdout comes back into your context, so sensitive content must not appear there.
4. Don't read its output files afterward. Report the path to the user and stop.
5. If the user asks you to look at the content directly, point out it would leave the device via your context, and confirm before proceeding.

The 35B model takes ~30s to load if cold and generates slower than cloud models — use a long timeout or `run_in_background`.

## `review` — independent second opinion

A reviewer from a different model lineage checks work you (Claude) produced. Default Kimi K3; `openai/gpt-5.6-sol` is the alternate (note: it reserves 128k output tokens per request, which can trip OpenRouter's 402 "requires more credits" daily-limit error — if that happens, use Kimi or ask the user to raise the key's daily limit).

```bash
cd <repo-root> && pi -p --provider openrouter --model moonshotai/kimi-k3 \
  --thinking high --exclude-tools edit,write --session-id delegate-review "<brief>"
```

- `--exclude-tools edit,write` keeps the reviewer read-only — it inspects, you decide what to apply.
- Brief it with what changed and how to see it, e.g.: "You are an independent code reviewer. Review the uncommitted changes (git diff HEAD) in this repo, which implement X. Look for bugs, design problems, and missed edge cases. Be critical; don't rubber-stamp. Report findings with file:line."
- Relay its findings honestly, including criticism of your own work, then give your own take on each finding — agree, rebut with reasons, or fix.

## `bulk` — cheap high-volume grunt work

For mountains of simple work that doesn't need much intelligence: reviewing lots of content, generating test/sample data, mechanical rewrites. Never for privacy-sensitive data — that's `private`.

```bash
pi -p --provider openrouter --model google/gemini-2.5-flash-lite --no-session "<brief>"
```

- `google/gemini-2.5-flash-lite` is near-free, reliable, and passes the account's ZDR policy. Truly free models exist (`pi --list-models ":free"`, e.g. `z-ai/glm-5.2:free`) but are shared-pool rate-limited (frequent 429s) and most lack ZDR endpoints, so the account rejects them (see ZDR note above). Prefer flash-lite.
- Use `--no-session` — bulk items don't need memory. Add `--no-tools` when the task is pure text generation (faster, no risk of it wandering the filesystem).
- Fan out for volume: split the work into items and run pi calls in parallel, e.g. `xargs -P 8`, each writing to its own output file. Spot-check a sample of outputs yourself before declaring the batch done.

## Adding a new agent

Extend the roster by editing this file: add a table row and a section with the exact command. Find models with `pi --list-models <search>` (OpenRouter exposes most cloud models; `~z-ai/glm-latest`-style aliases track the newest version). Prefer `pi -p --provider openrouter --model <id> --session-id delegate-<name>` as the template.

## Reporting back

- Lead with the delegate's result, clearly attributed ("GLM found 3 issues: …", "GPT 5.6 Sol's review: …").
- Send generated files with SendUserFile.
- These delegations cost real money (except `private`) — don't loop them unattended without the user asking.
