---
name: delegate-image
description: Generate an image via a panel of the 3 top-ranked OpenRouter image models in parallel, then have two independent AI judges each critique and pick their favorite. Use when the user asks to generate a logo, product shot, photorealistic image, or edit an image.
argument-hint: <image description>
---

# Delegate: image generation panel

Claude models can't generate images. This delegates to a **panel of 3 image-generation models run in parallel**, followed by **2 independent vision-model judges** that each critique and pick a favorite — so the user sees every option plus outside opinions, not just one model's guess.

Joe generates images rarely, so the 3-model panel is the default even though it costs ~3x a single generation (~$0.24 total) — don't downgrade to a single cheap model to save money unless asked.

All calls route through `pi` (already configured with the user's OpenRouter key) — never ask for or echo API keys.

**Zero data retention (ZDR):** the user's OpenRouter account rejects non-ZDR endpoints. This is why OpenAI's image models (`gpt-5.4-image-2`, `gpt-5-image`, `gpt-5-image-mini`) aren't in the roster below — they have no ZDR endpoint on OpenRouter and 404. Don't suggest loosening the account policy to use them.

## The roster (benchmarked 2026-09-01)

Only Google Gemini models actually generate images on OpenRouter — GPT Sol/Terra, Meta Muse, and Minimax M3 accept image input but don't output images; no Qwen image model exists there. Of Gemini's 4 tiers, a blind panel test (4 prompts: 2 logos, 2 photorealistic scenes, judged by Kimi with model identity hidden) ranked:

| Rank | Model | Avg blind rank | Notes |
|---|---|---|---|
| 1 | `google/gemini-3.1-flash-image` | 1.8 | Won 3 of 4 test prompts; best all-rounder |
| 2 | `google/gemini-2.5-flash-image` ("nano banana") | 2.0 | Won the photorealistic nature shot |
| 3 | `google/gemini-3-pro-image` ("nano banana pro") | 3.2 | Won the logo test; most detail-dense on complex scenes; priciest (~$0.14/img) |

`google/gemini-3.1-flash-lite-image` was dropped — it ranked last on all 4 test prompts despite being cheapest. Price didn't track quality in this test; Pro's higher detail didn't reliably beat Flash.

## Execution — one Agent call, one clean response

Treat this skill like a function call: the user invokes it and expects **3 images + 2 quick critiques back in a single response**, not a play-by-play. All the mechanics (generation, judging, retries, sanity-checking judges) happen inside **one Agent tool call** (default general-purpose agent). The Agent call runs asynchronously and returns via a task-notification, not inline — so after dispatching it, say nothing further and just wait. Don't narrate intermediate steps, don't use ScheduleWakeup or poll for progress, don't send an interim "generating now" message. The single notification that arrives when it finishes is your cue to write the one final reply.

Dispatch a single Agent call with a fully self-contained prompt (the subagent starts with zero context), something like:

```
Generate an image panel for: "<prompt, expanded from the user's ask: subject, style, composition, background, lighting>"

1. Run `python3 <skill-dir>/scripts/image-panel.py "<prompt>" <output-dir>` — generates flash.png, nano-banana.png, pro.png in parallel (~30-120s).
2. Run two independent judge critiques SEQUENTIALLY (not in parallel — concurrent calls to the same model can trip OpenRouter's credit hold):
   cd <output-dir> && pi -p --no-tools --no-session --provider openrouter --model moonshotai/kimi-k2.5 -- @flash.png @nano-banana.png @pro.png "These 3 images (in order: flash, nano-banana, pro) were each generated from the same prompt: '<prompt>'. For each, give a 1-sentence critique, then pick your favorite with a 1-sentence reason."
   ...then the same with --model z-ai/glm-4.6v.
   Before trusting either judge, confirm it actually has vision (`pi --list-models <name>` shows `images: yes`) and that its critique cites specific visual details rather than generic praise or the prompt/filenames restated — a vision-less model will fabricate a plausible-sounding critique instead of erroring (seen with kimi-k2-thinking). If a judge 402s ("requires more credits, or fewer max_tokens"), retry it alone, or swap to a smaller-max-output vision model (check the `max-out` column in `pi --list-models`).
3. Send all 3 images to the user via SendUserFile (display: render), one call, brief caption.
4. Return ONLY: each judge's pick + 1-sentence reason, your own 1-sentence recommendation, and total cost (sum from panel-manifest.txt). No step-by-step narration, no manifest dumps. If any image is a photorealistic depiction of a real identifiable person, say so in one line and note it wasn't published anywhere shareable.
```

To edit/reference an existing image instead of a fresh panel, skip the Agent dispatch and call `scripts/generate-image.py` directly with `-i input.png` on a single model — that's a quick single call, not worth delegating.

## After the Agent returns

Relay its result in **one short message**: which model each judge picked and why (one line each), your own take, and the cost — that's it. Don't re-explain the roster, the judge mechanics, or repeat what's already visible in the sent images.
