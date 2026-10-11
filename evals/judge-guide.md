# Level 2 — Automated Evaluation with LLMs

**Goal:** scale source-based answer review and measure how the judge agrees with independent human decisions. A working judge is not yet a calibrated judge.

## Implemented pilot

- `evals/judge.py`: versioned prompt, strict structured result and validation.
- `evals/run_judge.py`: freezes a bounded set of completed LangSmith traces, snapshots the rubric/prompt and runs the judge once per trace. Existing reviews and corrections are excluded from model input. No feedback is written to `answer_pass` or `review_reason`.
- `evals/calibration.py`: immutable first human reviews, reveal tracking, and comparison metrics.
- Shiny **Blind review**: shows the frozen conversation and evidence without prior labels, prior reasons, trace links or judge outcomes. The full frozen rubric is in the batch folder.

The first pilot used `gpt-5.4-mini`, medium reasoning, on 10 existing traces. All 10 API results finished and passed schema/source-reference checks. Usage: 49,365 input tokens and 5,052 completion tokens, 54,417 total. This is usage, not a dollar billing estimate. Using the same model family for answer generation and judging can share blind spots; this pilot establishes the workflow, not model superiority or expert alignment.

Batch: `evals/judge_runs/20260908T093514688801Z/`.

The batch contains traces previously discussed or labeled by the assistant. It is a development/practice batch, not a fresh independent holdout. A reviewer who has seen prior labels must not mark those reviews independent. Domain-sensitive disagreements still need a qualified reviewer.

## How to use the English UI

Open http://127.0.0.1:8001 and choose **Blind review · …** under Data source.

1. Read the current answer, history and sources. Judge the entire answer using the rubric.
2. Check **I have not seen earlier labels or critiques for this trace** only when true. It defaults off. Leaving it off still allows a practice review, excluded from independent metrics.
3. Select Pass/Fail; a Fail needs a reason. Skip when you cannot decide.
4. Use **Save without moving** if you want to compare this case immediately. The first human decision is locked to preserve what you believed before seeing the judge.
5. Click **Reveal judge after saving**. Only then does the server send the judge verdict, concise rationale and quoted issues to the browser. This is not just CSS hiding.
6. Read disagreements as candidates for adjudication: the judge, human label, or rubric may need correction. The machine is not the answer key.

**Save & next** supports reviewing a queue before returning to individual results. Revisiting a row does not automatically expose its judge outcome. Normal LangSmith review and local eval modes are still available; blind review never overwrites those labels.

Human reviews are stored in `evals/labels/calibration.sqlite3`, with batch ID, run ID, input hash and rubric hash. Reveal events are recorded across batches for the same run/input. A later review of already revealed content is excluded even if its checkbox claims independence. The UI cannot detect what the reviewer saw outside this app; independence remains self-reported. Editing after reveal cannot overwrite the initial label. Any later adjudication needs its own record/process rather than replacing the first blind decision.

## Running and measuring

```bash
# Explicit paid judge run; does not regenerate the RAG answers.
make judge

# Read current comparisons without any model or cloud calls.
.venv/bin/python -m evals.calibration --batch 20260908T093514688801Z
```

`OPENAI_JUDGE_MODEL` optionally overrides the configured answer model. No automatic retry occurs. A failed call, refusal, truncated response, malformed result, nonexistent source rank or invented quoted claim does not become Pass/Fail. The runner stops after the first error, persists an incomplete batch, and does not expose it as a complete calibration queue. Inspect the saved failure before explicitly starting another paid run.

The judge can abstain with `verdict=null` and `needs_human_review=true`. This is an operational needs-review status, not a third quality rating. Its reason is kept; it is excluded from binary metrics.

Metrics treat **Fail as the positive class**:

- TP: human Fail, judge Fail.
- FP: human Pass, judge Fail.
- FN: human Fail, judge Pass.
- TN: human Pass, judge Pass.
- Failure precision = TP / (TP + FP).
- Failure recall = TP / (TP + FN).

The script excludes missing human labels, self-reported previously exposed labels, and judge abstentions/errors, reporting counts for these cases. Abstention/error counts in this comparison apply to eligible human-reviewed cases. Zero denominators produce `null` / N/A, never a made-up perfect score. The UI hides aggregate comparisons until the queue has human reviews, so results cannot guide the remaining first labels. The CLI is intended for analysis after reviewing; opening raw judge files or using external tools can of course reveal results.

At implementation time there are **0 independent human pairs**: precision, recall and agreement are N/A. We have not used assistant labels as human gold.

## What is still required to complete this stage

1. Collect genuinely independent human labels, with specialist adjudication where needed. The existing previously exposed cases are useful for practice, not sufficient for an unbiased estimate.
2. Review disagreements without assuming either side is correct. Explicitly clarify rubric ambiguities, including how much support an extra claim needs.
3. Iterate judge prompts on a development set. Keep the original prompt/results and do not quietly relabel the comparison set.
4. Evaluate on new held-out conversations/case families, not paraphrases of development questions. No validated held-out split exists yet.
5. Track precision/recall, coverage, small-sample uncertainty, cost and latency. Periodically audit new traces with humans as data/model behavior changes.

No RAG prompt or retriever has been changed as part of this judge pilot. Building the evaluator and improving the product are related but separate experiments.

Official implementation references: [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini). The current model supports structured outputs; schema validity does not establish semantic judgment quality.

## Latest validation — 2026-09-08

Judge v3 remains the default; `evals.claim_judge` is experimental. Repeated validation on 8 new synthetic assistant-labeled cases matched all labels in three runs. This is a small controlled check, not human calibration or production accuracy. Known long-answer judgments have varied across runs. See [the report](judge_experiments/20260908-stability/report.md).

Recompute metrics without API calls:

```bash
.venv/bin/python -m evals.summarize_repeats evals/judge_experiments/20260908-stability
```

Use scores to assist review. Keep human expert calibration open; do not treat assistant labels as expert gold. Recheck after model/prompt/rubric changes and add fresh examples beyond development cases.
