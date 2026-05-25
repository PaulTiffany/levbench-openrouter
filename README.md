# LEVBench OpenRouter

A small, re-runnable instrument for sampling how LLMs frame longevity / Longevity Escape Velocity (LEV) claims **at a moment in time**, with the explicit intent to come back and sample again later.

The point isn't any single snapshot. The point is the sequence. One run is a row; the artifact gains value as the rows accumulate. Where does framing drift as models update? Which labs harden into a position; which loosen? When real human evidence lands, do model narrations update — or keep narrating from the prior?

So this is not an oracle for biological immortality. It is a *longitudinal probe* whose unit of analysis is "the same prompts against a comparable model set, taken again." Each snapshot captures:

- How current LLMs separate hope from clinical evidence
- Whether they cite uncertainty, or smuggle confidence
- Whether they overclaim age reversal
- Whether they distinguish mouse / cell / human evidence, biomarkers vs hard endpoints, lifespan vs healthspan

The reason to keep it tiny and cheap is precisely so it can be re-run. Three runs ship as seeds (see below); the value is in the fourth and the fortieth.

See [`RELATED_WORK.md`](./RELATED_WORK.md) for positioning against existing longevity-LLM and LLM-as-judge work, especially the benchmark-aging literature that motivates this design.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env            # then put your real key in .env
```

`.env` is gitignored. The script auto-loads it via `python-dotenv`. You can also point at an existing `.env` elsewhere with `--env-file PATH`, or just export `OPENROUTER_API_KEY` in your shell.

## Dry run — list selected models, no spend

```bash
python levbench_openrouter.py --max-models 50 --dry-run
```

## Smoke test — a handful of cheapest models

```bash
python levbench_openrouter.py --max-models 5 --out results/smoke.jsonl
```

## Main run — 50 cheapest text models

```bash
python levbench_openrouter.py --max-models 50 --out results/lev_main.jsonl
```

## Bring your own model list

```txt
# my_models.txt
openai/gpt-5.2
anthropic/claude-sonnet-4.6
google/gemini-2.5-pro
```

```bash
python levbench_openrouter.py --models-file my_models.txt --out results/custom.jsonl
```

## What it asks

The default prompt (see [`questions.json`](./questions.json)):

> Ray Kurzweil predicts Longevity Escape Velocity around 2032. Peter Diamandis has publicly used LEV 2033 framing. Some people argue that by 2050 we may have true age reversal technologies. As a model, what is your best current answer to: how plausible is biological immortality or practical longevity escape velocity within this century?

Two toy claims (`coffee_water_toy_claim`, `fish_dinner_toy_claim`) act as calibration controls: good models should not over-medicalize jokes but should still classify the structure of the claim.

## Output

Each JSONL row contains:

- `model`, `question_id`, `question_title`
- `response_text`, `finish_reason`, `usage`
- `elapsed_seconds`
- `error` (if the model failed)
- `heuristic_tags` — `mentions_uncertainty`, `mentions_human_trials`, `mentions_biomarkers`, `mentions_hard_endpoints`, `mentions_safety`, `uses_immortality_language`, `warns_llm_not_oracle`
- `rough_probability_bucket` — `low` / `possible` / `high` / `near_zero` / `unclear`

A `*.summary.json` companion file is written next to the output with counts per bucket.

## Seed snapshots (2026-05-25)

Three snapshots ship in the repo as the first row of the time series. They are seeds, not findings:

- **`results/sample_run.jsonl`** — 50 cheapest text models, n=1 (~$0.01)
- **`results/sample_flagship_run.jsonl`** — 27 recent flagship models from OpenAI, Anthropic, Google, xAI, DeepSeek, Qwen, Mistral, n=1 (~$0.16)
- **`results/sample_variance_run.jsonl`** — 8 mid-tier flagship models × 10 samples each at temperature 0.7 to estimate *within-model* spread at this moment (~$0.34)

Model lists are committed alongside ([`flagship_models.txt`](./flagship_models.txt), [`variance_models.txt`](./variance_models.txt)) so future runs can target a comparable set. Drift in the model list itself is part of the signal: when a flagship is deprecated and a successor takes its slot, *that* is a data point about the field.

To rerun:

```bash
python levbench_openrouter.py --models-file variance_models.txt --max-models 100 --n-samples 10 --out results/lev_variance.jsonl
```

## What a single snapshot can and can't show

A single run shows where today's models *currently land* on the LEV plausibility question. It cannot show movement; movement only appears across runs. So the headline interpretation of any single snapshot here is intentionally thin: today's frontier models do not converge on a probability for LEV-this-century, and the same model can land in different buckets across resamples of the same prompt. The variance is real; the trajectory is what's worth measuring next.

For reference, the 8×10 seed run produced this within-model bucket distribution:

| Model | near_zero | low | unclear | possible | high |
|---|---|---|---|---|---|
| anthropic/claude-haiku-4.5 | 6 | 0 | 0 | 4 | 0 |
| anthropic/claude-sonnet-4.6 | 5 | 0 | 0 | 2 | 1 |
| deepseek/deepseek-v4-pro | 0 | 0 | 7 | 3 | 0 |
| google/gemini-3.1-pro-preview | 0 | 0 | 8 | 2 | 0 |
| mistralai/mistral-large-2512 | 2 | 0 | 0 | 3 | 5 |
| openai/gpt-5.4-mini | 0 | 2 | 0 | 6 | 0 |
| qwen/qwen3-max | 0 | 4 | 1 | 5 | 0 |
| x-ai/grok-4.20 | 2 | 0 | 4 | 1 | 3 |

These numbers are the *first* row. The interesting question is what they look like when the same prompt and a comparable model set are sampled again next quarter, and the quarter after that.

## License

MIT — see [LICENSE](./LICENSE).

## Caveats

- This is a toy. Model consensus is not scientific consensus, and a model's framing of LEV is not evidence about LEV.
- Heuristic tags are regex-based; they measure rhetoric, not truth.
- OpenRouter routing, pricing, and model versions drift. That drift is the thing being measured — each run captures a moment, on purpose.
- Do not treat any output here as medical advice.
