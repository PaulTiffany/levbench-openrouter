# LEVBench OpenRouter

A tiny, time-stamped benchmark that asks many OpenRouter models the same longevity / Longevity Escape Velocity (LEV) question and saves their raw answers as JSONL.

It is deliberately **not** an oracle for biological immortality. It is a *consistency probe*:

- What do current LLMs say when asked identical LEV / longevity questions?
- Do they separate hope from clinical evidence?
- Do they cite uncertainty?
- Do they overclaim age reversal?
- Do they distinguish mouse / cell / human evidence, biomarkers vs hard endpoints, lifespan vs healthspan?

See [`RELATED_WORK.md`](./RELATED_WORK.md) for positioning against existing longevity-LLM and LLM-as-judge work.

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

## A curated sample run lives in `results/sample_run.jsonl`

So you can see the shape of the output without spending anything.

## Caveats

- This is a toy. Model consensus is not scientific consensus.
- Heuristic tags are regex-based; they measure rhetoric, not truth.
- OpenRouter routing, pricing, and model versions drift. Every run captures a moment.
- Do not treat any output here as medical advice.
