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

## Step 1 — generate the panel

```bash
python3 <skill-dir>/scripts/image-panel.py "<detailed prompt>" <output-dir>
```

Runs all 3 models in parallel, saves `flash.png`, `nano-banana.png`, `pro.png` into `<output-dir>`, and writes `panel-manifest.txt` with per-model cost (via OpenRouter's usage accounting — no guessing at list prices). Takes 30–120s; use a generous Bash timeout.

Write the prompt yourself, expanded from the user's ask: subject, style, composition, background, lighting. To edit/reference an existing image, use `scripts/generate-image.py` directly on a single model with `-i input.png` (the panel script doesn't support image input).

## Step 2 — two independent judges

Use two vision-capable models from **different lineages than the generators** (both Google) and from each other, so critiques aren't circular. Defaults, chosen for small max-output (avoids OpenRouter's per-request credit-hold rejecting the call on a constrained daily limit — less of a concern now that the user has topped up credits, but still fine defaults):

```bash
cd <output-dir> && pi -p --no-tools --no-session --provider openrouter --model moonshotai/kimi-k2.5 \
  -- @flash.png @nano-banana.png @pro.png \
  "These 3 images (in the order: flash, nano-banana, pro) were each generated from the same prompt: '<prompt>'. For each, give a 1-sentence critique, then pick your favorite with a 1-sentence reason."
```

```bash
cd <output-dir> && pi -p --no-tools --no-session --provider openrouter --model z-ai/glm-4.6v \
  -- @flash.png @nano-banana.png @pro.png \
  "These 3 images (in the order: flash, nano-banana, pro) were each generated from the same prompt: '<prompt>'. For each, give a 1-sentence critique, then pick your favorite with a 1-sentence reason."
```

Run these sequentially, not in parallel — concurrent calls to the same model can trip OpenRouter's per-request credit hold even with balance available (seen in testing: two 131k-max-output calls in flight at once got rejected individually even though neither alone would fail). If a judge call 402s ("requires more credits, or fewer max_tokens"), it's an output-token reservation issue, not an out-of-money one — retry the same call alone, or swap in a model with a smaller max-output (check `pi --list-models <name>`, the `max-out` column).

**Verify the judge actually looked at the images before trusting it.** A text-only model (no vision) will still return a plausible-sounding critique instead of an error — caught in testing with `kimi-k2-thinking`, which fabricated a critique from the filenames alone. Check `pi --list-models <name>` shows `images: yes` before using a model as a judge, and sanity-check that its critique cites specific visual details (not just generic praise) rather than restating the prompt or filenames back.

## Reporting back

- Send all 3 images to the user with SendUserFile (`display: render`) — don't pick one for them.
- Report each judge's pick and reasoning, clearly attributed by model name.
- Give your own read too: which fits the user's actual use case (e.g. Pro tends to win on logos/icons; Flash tends to win on photorealistic scenes — but check this per-prompt, don't just default to the table above).
- **Photorealistic images of real, identifiable people**: flag this explicitly. These can be strikingly convincing, including fabricated real-world details (signage, brands). Don't include them in a published Artifact or anything shareable — send as plain files only, and note they're synthetic.
