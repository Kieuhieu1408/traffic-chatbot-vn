# Qwen RAG learning pilot

Goal: compare the same small model before/after training, separating fixed evidence from real retrieval. This pilot is not intended to beat GPT-5.4 mini or certify legal correctness.

## Data and curation

`prepare.py` builds 16 training examples (8 originals including no-evidence controls, plus train-only wording variants), 5 development examples and 6 test examples. Document groups are disjoint: 12/2017 train, 29/2015 dev, 31/2019 test. PDF/DOCX versions inherit the same document group. Sources are exact spans, checked against corpus; target answers are assistant-curated, not expert gold. No old Pass label is imported automatically.

Known gaps: tiny sample, no comparison/multi-turn tasks, and tables appear only in test. Splitting by document changes topic distribution. Test examples are familiar to the assistant from prior work, though not used for adapter optimization. Treat results as a mechanics pilot, not an unbiased product benchmark.

## Frozen experiment

Qwen3-1.7B checkpoint downloaded to local HF snapshot, 4-bit NF4 double quantization, BF16 compute, non-thinking chat template, greedy generation, max 192 new tokens. Fixed context budget: input <=2048; no silent truncation. Real retrieval selects whole chunks in rank order within 1400 input tokens; omitted IDs are logged. Same input settings and packing before/after.

QLoRA pilot: q_proj/v_proj, rank 8, alpha 16, dropout .05; learning rate 1e-4, 3 epochs, batch 1, accumulation 4, seed 42. These are fixed teaching settings, not optimized on test. Only assistant-target tokens contribute to loss. Save adapter separately; do not modify the deployed GPT model or RAG behavior.

## Commands

Environment: separate `.venv-ft`, Python 3.12, CUDA PyTorch. Main `.venv` continues serving retrieval and evaluation utilities.

```bash
.venv/bin/python finetune/prepare.py
PYTHONPATH=. .venv/bin/python finetune/retrieval_eval.py
.venv-ft/bin/python finetune/run.py baseline --model-path /absolute/hf/snapshot
.venv-ft/bin/python finetune/run.py train --model-path /absolute/hf/snapshot
.venv-ft/bin/python finetune/run.py after --model-path /absolute/hf/snapshot
```

Run outputs cannot overwrite existing baseline/after files. Config and dataset hashes must match. Confirm complete baseline outputs before using a training run as a comparison.

Retrieval report initially checks known evidence at K=1,3,6,10 and reciprocal rank; unmatched sources are unjudged. Precision@K is intentionally not reported until relevance judgments are sufficient. These lower-bound evidence checks are not exhaustive recall or relevance gold.

Sources for implementation: [Qwen model card](https://huggingface.co/Qwen/Qwen3-1.7B), [PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization).
