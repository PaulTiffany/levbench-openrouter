#!/usr/bin/env python3
"""
LEVBench OpenRouter toy benchmark.

Asks many OpenRouter models the same longevity question and stores raw responses as JSONL.

Required:
  export OPENROUTER_API_KEY="..."

Examples:
  python levbench_openrouter.py --dry-run --max-models 50
  python levbench_openrouter.py --max-models 5 --out results/smoke_test.jsonl
  python levbench_openrouter.py --question-id coffee_water_toy_claim --max-models 10
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_APP_TITLE = "LEVBench Toy Benchmark"

SYSTEM_PROMPT = """You are answering a longevity-science plausibility question.
Be careful, non-hypey, and specific about uncertainty.
Do not present yourself as an oracle.
Do not provide medical advice.
Distinguish biological plausibility, human clinical evidence, biomarkers, hard endpoints, and futurist timelines.
"""


def load_questions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("questions.json must contain a list")
    return data


def pick_question(questions: List[Dict[str, Any]], question_id: str) -> Dict[str, Any]:
    for q in questions:
        if q.get("question_id") == question_id:
            return q
    raise KeyError(f"question_id not found: {question_id}")


def auth_headers() -> Dict[str, str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://example.local/levbench",
        "X-OpenRouter-Title": DEFAULT_APP_TITLE,
    }


def fetch_models(require_key: bool = True) -> List[Dict[str, Any]]:
    headers = auth_headers() if require_key else {"Content-Type": "application/json"}
    r = requests.get(f"{OPENROUTER_BASE}/models", headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json().get("data", [])
    if not isinstance(data, list):
        raise RuntimeError("Unexpected models response")
    return data


def price_as_float(model: Dict[str, Any], field: str) -> float:
    try:
        return float(model.get("pricing", {}).get(field, "999999"))
    except Exception:
        return 999999.0


def is_text_model(model: Dict[str, Any]) -> bool:
    arch = model.get("architecture", {}) or {}
    out = arch.get("output_modalities", []) or []
    mod = arch.get("modality", "") or ""
    return "text" in out or "text->text" in mod


def auto_select_models(
    models: List[Dict[str, Any]],
    max_models: int,
    include_free: bool,
    free_only: bool,
    require_temperature: bool,
) -> List[str]:
    selected: List[Dict[str, Any]] = []
    for m in models:
        mid = m.get("id")
        if not mid or not is_text_model(m):
            continue
        supported = set(m.get("supported_parameters") or [])
        if require_temperature and "temperature" not in supported:
            continue

        is_free_id = str(mid).endswith(":free")
        prompt_cost = price_as_float(m, "prompt")
        completion_cost = price_as_float(m, "completion")
        is_zero_price = prompt_cost == 0 and completion_cost == 0
        is_free = is_free_id or is_zero_price

        if free_only and not is_free:
            continue
        if not include_free and is_free:
            continue
        selected.append(m)

    # Cheap first, then shorter context last-resort. This is not a quality ranking.
    selected.sort(
        key=lambda m: (
            price_as_float(m, "prompt") + price_as_float(m, "completion"),
            -(m.get("context_length") or 0),
            str(m.get("id", "")),
        )
    )
    return [m["id"] for m in selected[:max_models]]


def load_models_file(path: Path) -> List[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def call_model(model: str, prompt: str, max_tokens: int, timeout: int, temperature: float = 0.0) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    started = time.time()
    try:
        r = requests.post(
            f"{OPENROUTER_BASE}/chat/completions",
            headers=auth_headers(),
            json=payload,
            timeout=timeout,
        )
    except requests.exceptions.RequestException as exc:
        return {
            "model": model,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": {"exception": type(exc).__name__, "message": str(exc)[:500]},
        }
    elapsed = time.time() - started
    if r.status_code >= 400:
        return {
            "model": model,
            "elapsed_seconds": round(elapsed, 3),
            "error": {
                "status_code": r.status_code,
                "body": safe_body(r),
            },
        }
    body = r.json()
    choice = (body.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    return {
        "model": model,
        "elapsed_seconds": round(elapsed, 3),
        "response_text": content,
        "finish_reason": choice.get("finish_reason"),
        "native_finish_reason": choice.get("native_finish_reason"),
        "usage": body.get("usage"),
        "raw_response_model": body.get("model"),
        "error": None,
    }


def safe_body(r: requests.Response) -> Any:
    try:
        return r.json()
    except Exception:
        return r.text[:2000]


def heuristic_tags(text: str) -> Dict[str, bool]:
    t = text.lower()
    return {
        "mentions_uncertainty": any(w in t for w in ["uncertain", "uncertainty", "speculative", "unknown", "plausible", "probability", "chance"]),
        "mentions_human_trials": any(w in t for w in ["human trial", "clinical trial", "randomized", "phase ii", "phase iii"]),
        "mentions_biomarkers": any(w in t for w in ["biomarker", "epigenetic", "methylation", "surrogate endpoint"]),
        "mentions_hard_endpoints": any(w in t for w in ["mortality", "morbidity", "lifespan", "healthspan", "function", "frailty"]),
        "mentions_safety": any(w in t for w in ["safety", "risk", "adverse", "side effect", "regulatory"]),
        "uses_immortality_language": any(w in t for w in ["immortal", "immortality", "indefinite lifespan", "escape velocity"]),
        "warns_llm_not_oracle": any(w in t for w in ["oracle", "judge", "llm", "model consensus", "not evidence"]),
    }


def rough_probability_bucket(text: str) -> str:
    """Very rough regex extraction for post-hoc sorting, not scientific scoring."""
    t = text.lower()
    if re.search(r"\b(very unlikely|unlikely|low chance|not likely)\b", t):
        return "low"
    if re.search(r"\b(plausible|possible|nonzero|could happen)\b", t):
        return "possible"
    if re.search(r"\b(likely|probable|more likely than not)\b", t):
        return "high"
    if re.search(r"\b(no|near zero|impossible)\b", t):
        return "near_zero"
    return "unclear"


def write_jsonl_row(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize_jsonl(path: Path) -> Dict[str, Any]:
    rows = []
    if not path.exists():
        return {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    ok = [r for r in rows if not r.get("error")]
    err = [r for r in rows if r.get("error")]
    buckets: Dict[str, int] = {}
    for r in ok:
        b = r.get("rough_probability_bucket", "unclear")
        buckets[b] = buckets.get(b, 0) + 1
    return {
        "total_rows": len(rows),
        "successful": len(ok),
        "errors": len(err),
        "rough_probability_buckets": buckets,
    }


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a tiny OpenRouter multi-model LEV benchmark.")
    parser.add_argument("--questions", default="questions.json", help="Path to questions.json")
    parser.add_argument("--question-id", default="lev_century_plausibility", help="Question id to run")
    parser.add_argument("--models-file", help="Optional text file: one OpenRouter model id per line")
    parser.add_argument("--max-models", type=int, default=50, help="Number of models to run")
    parser.add_argument("--include-free", action="store_true", help="Include free models in auto-selection")
    parser.add_argument("--free-only", action="store_true", help="Only use free models in auto-selection")
    parser.add_argument("--no-require-temperature", action="store_true", help="Do not filter for temperature support")
    parser.add_argument("--max-tokens", type=int, default=700, help="Max output tokens per model")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout seconds per model")
    parser.add_argument("--sleep", type=float, default=0.5, help="Seconds between model calls")
    parser.add_argument("--n-samples", type=int, default=1, help="Independent samples per model (for within-model variance)")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature. Default: 0.0 if n-samples==1 else 0.7")
    parser.add_argument("--dry-run", action="store_true", help="List selected models only")
    parser.add_argument("--out", default="results/levbench_results.jsonl", help="Output JSONL path")
    parser.add_argument("--env-file", help="Path to a .env file to load OPENROUTER_API_KEY from")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if load_dotenv is not None:
        if args.env_file:
            load_dotenv(args.env_file, override=False)
        else:
            load_dotenv(override=False)

    questions = load_questions(Path(args.questions))
    question = pick_question(questions, args.question_id)

    if args.models_file:
        model_ids = load_models_file(Path(args.models_file))[: args.max_models]
    else:
        models = fetch_models(require_key=not args.dry_run)
        model_ids = auto_select_models(
            models=models,
            max_models=args.max_models,
            include_free=args.include_free,
            free_only=args.free_only,
            require_temperature=not args.no_require_temperature,
        )

    print(f"Question: {question['question_id']} — {question.get('title', '')}")
    print(f"Selected {len(model_ids)} model(s):")
    for mid in model_ids:
        print(f"  - {mid}")

    if args.dry_run:
        return 0

    out_path = Path(args.out)
    prompt = question["prompt"]
    temperature = args.temperature if args.temperature is not None else (0.0 if args.n_samples == 1 else 0.7)
    total_calls = len(model_ids) * args.n_samples
    call_idx = 0

    for model in model_ids:
        for sample_idx in range(args.n_samples):
            call_idx += 1
            print(f"[{call_idx}/{total_calls}] {model} (sample {sample_idx + 1}/{args.n_samples})", flush=True)
            result = call_model(model, prompt, max_tokens=args.max_tokens, timeout=args.timeout, temperature=temperature)
            row = {
                "question_id": question["question_id"],
                "question_title": question.get("title"),
                "model": model,
                "sample_idx": sample_idx,
                "temperature": temperature,
                **result,
            }
            if not row.get("error"):
                tags = heuristic_tags(row.get("response_text", ""))
                row["heuristic_tags"] = tags
                row["rough_probability_bucket"] = rough_probability_bucket(row.get("response_text", ""))
            write_jsonl_row(out_path, row)
            time.sleep(args.sleep)

    summary = summarize_jsonl(out_path)
    summary_path = out_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote: {out_path}")
    print(f"Summary: {summary_path}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
