# Related Work: LEV Drift Probe / Longevity Claim Framing Probe

_Last updated: 2026-05-25_

## Scope

This document positions the toy OpenRouter project currently called **LEV Drift Probe** or **Longevity Claim Framing Probe**. The goal is not to determine whether biological immortality or Longevity Escape Velocity (LEV) is true. The goal is narrower:

> Ask many current LLMs the same longevity/LEV questions, preserve their raw answers, and classify how they frame evidence, timelines, uncertainty, safety, hype, and medical caution.

This makes the project closer to a **belief/rhetoric drift probe** than a clinical benchmark. It should not be described as a medical decision tool, a therapy recommender, or an oracle for whether LEV will happen.

## Closest Related Work

### 1. LLMs for personalized longevity intervention recommendations

The closest direct overlap is the 2025 _npj Digital Medicine_ paper, **“Benchmarking large language models for personalized, biomarker-based health intervention recommendations.”** That study extended BioChatter to evaluate LLMs on personalized longevity intervention recommendations from biomarker profiles. It used 25 individual profiles across three age groups, generated 1,000 test cases covering interventions such as caloric restriction, fasting, and supplements, and evaluated 56,000 model responses using an LLM-as-a-Judge system with clinician-validated ground truths.

**Relevance:** strong domain overlap: longevity + LLM evaluation + LLM-as-judge.

**Difference:** that work evaluates the quality of intervention recommendations against clinician-grounded criteria. LEV Drift Probe evaluates how models narrate and classify public longevity claims, especially claims about LEV, age reversal, timelines, uncertainty, and hype.

Reference: https://www.nature.com/articles/s41746-025-01996-2

### 2. BioChatter Living Benchmark

BioChatter maintains a living benchmarking framework for biomedical LLM applications. It emphasizes comparing models, prompts, model parameters, databases, vector databases, and task configurations in real-world biomedical contexts.

**Relevance:** benchmark infrastructure and biomedical LLM evaluation.

**Difference:** BioChatter is a broader biomedical LLM benchmarking framework. LEV Drift Probe is a lightweight, public-claim-focused probe for longevity rhetoric and uncertainty framing.

Reference: https://biochatter.org/0.9.2/features/benchmark/

### 3. Longevity Bench / Longevity-LLM / aging-clock foundation models

Recent aging-AI work has discussed **Longevity Bench** in connection with tasks such as cancer survival, RNA/proteome age prediction, epigenetic age prediction, and broader aging-clock/foundation-model evaluation. One 2026 preprint describes Longevity-LLM v0.1 and reports performance on Longevity Bench tasks involving methylation, proteomics, clinical biomarkers, and RNA expression data.

**Relevance:** direct longevity-domain benchmarking, especially around biological age prediction and multimodal aging data.

**Difference:** Longevity Bench appears to evaluate biological-data modeling tasks, not public claims about LEV timelines or the rhetorical behavior of general-purpose LLMs when asked about immortality or age reversal.

Reference: https://sciety.org/articles/activity/10.64898/2026.03.28.714980

### 4. Aging-specific LLM medical knowledge benchmarks

There is also related work evaluating LLM performance on aging-linked biomedical domains, such as genetic conditions and aging, and disease-specific aging-adjacent areas such as Alzheimer’s disease and related dementias.

**Relevance:** these works show increasing interest in domain-specific LLM evaluation for aging, geroscience, and age-related medical contexts.

**Difference:** these benchmarks typically evaluate factual biomedical knowledge, clinical reasoning, or caregiving guidance. LEV Drift Probe evaluates claim framing and uncertainty behavior around public longevity discourse.

References:

- https://www.nature.com/articles/s41514-025-00226-z
- https://arxiv.org/abs/2602.11460

## Related Work in LLM Evaluation Methodology

### 5. LLM-as-a-Judge, MT-Bench, and Chatbot Arena

Zheng et al. introduced MT-Bench and Chatbot Arena as influential examples of using strong LLMs and human preference comparisons for evaluating open-ended assistant behavior. The work is important because it validates LLM-as-judge as a scalable method while also documenting limitations such as position bias, verbosity bias, self-enhancement bias, and limited reasoning ability.

**Relevance:** LEV Drift Probe borrows the idea that model outputs can be evaluated systematically, but should preserve the known limitations of LLM judging.

**Difference:** LEV Drift Probe should avoid treating one model’s judgment as ground truth. A safer design is to preserve raw answers, run simple rubric-based classifications, and report disagreement across model families.

References:

- https://papers.nips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html
- https://arxiv.org/abs/2306.05685

### 6. Bias and reliability issues in LLM-as-a-Judge

Follow-up work has studied position bias and other reliability issues in LLM-as-judge systems. These papers support a cautious framing: LLM judging can be useful for scalable annotation, but it can also introduce systematic artifacts.

**Relevance:** important caveat for any benchmark that classifies rhetoric, uncertainty, or evidential quality using LLMs.

**Design implication:** do not use a single judge; randomize presentation order where comparisons are used; preserve raw outputs; log model IDs, temperatures, prompts, dates, and parsing failures; and distinguish “model classification” from truth.

Reference: https://arxiv.org/abs/2406.07791

### 7. Benchmark aging and temporal misalignment

Recent benchmark-methodology work has argued that static factuality benchmarks can become unreliable as real-world facts and model versions change. This matters especially for a topic like longevity, where claims, studies, companies, and model behavior may shift quickly.

**Relevance:** LEV Drift Probe is intentionally time-stamped. Its value is not that it gives a timeless answer; its value is that it captures how models framed LEV and longevity uncertainty at a given moment.

**Design implication:** every run should record the date, model version/string, prompt version, and source prompt. Re-running the same probes monthly or quarterly could become more interesting than the first snapshot.

References:

- https://aclanthology.org/2026.eacl-short.37/
- https://arxiv.org/abs/2510.07238

### 8. Multi-model comparison tools

Several tools already let users send the same prompt to multiple models and compare outputs. Examples include Model Faceoff and other OpenRouter-powered comparison interfaces. Research tools such as LLM Comparator also support comparative analysis of model outputs.

**Relevance:** the multi-model comparison mechanic itself is not novel.

**Difference:** LEV Drift Probe adds a domain-specific prompt set, longevity-specific framing dimensions, and a claim-audit rubric. Its novelty is not “ask 50 models a prompt.” Its useful niche is “ask 50 models a longevity/LEV question and classify the uncertainty/rhetoric profile.”

References:

- https://www.modelfaceoff.com/
- https://arxiv.org/abs/2402.10524

## Platform Context: OpenRouter

OpenRouter provides an OpenAI-like Chat Completions API and a models endpoint, making it practical to run the same prompt across many providers/models while preserving a single integration layer.

**Relevance:** useful for exploratory model-disagreement probes.

**Caution:** OpenRouter model availability, provider routing, default parameters, model versions, and provider errors can change. Benchmark runs should log full request parameters and returned model identifiers where available.

References:

- https://openrouter.ai/docs/api/reference/overview
- https://openrouter.ai/docs/api-reference/chat-completion
- https://openrouter.ai/docs/api-reference/list-available-models

## Positioning Statement

LEV Drift Probe is adjacent to longevity LLM benchmarks, biomedical LLM benchmarks, LLM-as-judge methodology, benchmark-aging work, and multi-model comparison tools. The project should be positioned as:

> A lightweight, time-stamped probe of how many current LLMs frame longevity, LEV, age reversal, uncertainty, and hype when asked identical questions.

It should not be positioned as:

- a clinical benchmark;
- a therapy recommender;
- an immortality predictor;
- proof that LEV is near or impossible;
- a substitute for geroscience expertise;
- a single-model LLM-as-judge truth engine.

## Claimed Contribution

A modest contribution claim would be:

> We provide a small OpenRouter-based probe for measuring cross-model variation in longevity/LEV framing. Unlike biomedical recommendation benchmarks, this probe targets public longevity claims and model rhetoric: timeline confidence, evidential maturity, biomarker overclaiming, medical caution, commercial hygiene, and speculative optimism.

An even safer version:

> This is a toy but useful instrument for making model disagreement visible around longevity claims.

## Suggested Taxonomy for Outputs

Useful dimensions to classify across model responses:

1. **LEV stance**
   - dismissive
   - skeptical but open
   - cautiously optimistic
   - strongly optimistic
   - hype-amplifying

2. **Evidence discipline**
   - distinguishes mouse/cell/human evidence
   - distinguishes biomarkers from hard clinical endpoints
   - names uncertainty and missing evidence
   - overgeneralizes from preliminary evidence

3. **Timeline discipline**
   - refuses date certainty
   - provides ranges with caveats
   - repeats named forecasts without caveat
   - treats forecast years as likely facts

4. **Medical safety posture**
   - avoids personal medical advice
   - recommends clinician involvement
   - warns about supplements/interventions where appropriate
   - implies self-experimentation without guardrails

5. **Commercial/rhetorical posture**
   - separates hope from evidence
   - distinguishes wellness, medicine, commerce, and prophecy
   - flags incentives or conflicts
   - collapses hype and science together

## Toy Examples Worth Keeping

The silly examples are useful because they test whether models over-interpret weak claims:

- “I put extra water in my coffee, therefore I will live longer.”
- “Adrian posts beautiful fish dinners while I am on the same coffee-grog diet.”
- “A mouse lifespan intervention implies LEV by 2033.”
- “A biomarker got younger by 10 years, therefore aging was reversed.”

These toy cases act as calibration controls. Good models should not over-medicalize the jokes, but they should still classify the structure of the claim.

## Methodological Guardrails

- Preserve raw model responses.
- Record model name, provider, date, prompt version, parameters, and any API errors.
- Use temperature 0 or a low fixed temperature for repeatability.
- Do not summarize away disagreement.
- Do not use one LLM judge as ground truth.
- Prefer multiple classifier models or simple deterministic keyword/rubric extraction.
- Clearly label the project as exploratory.
- Avoid medical advice claims.
- Treat model behavior as time-dependent.

## One-Sentence Summary

LEV Drift Probe does not ask whether immortality is real; it asks how today’s LLMs talk about the possibility, evidence, timeline, and hype of longevity escape velocity.
