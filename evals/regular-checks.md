# Level 1, Step 3 — Run & Track Your Tests Regularly

**Goal:** After every modification, verify whether agreed behaviors remain intact and track which code and test versions generated the results.

## Workflow Cadence

1. Prior to making changes, run `make check` to establish a comparison baseline.
2. Modify a behavior and re-run `make check`. Inspect failing cases rather than just total passed tests. If test definitions are edited, check test hashes: the measurement tool itself has changed.
3. When modifying retrieval, chunking, embedding, or query parameters, additionally run `make eval-retrieval`. Compare each question against prior baselines on the same dataset/corpus/config. Config changes must be treated as experimental variables.
4. When modifying prompts or generation logic, logic tests are insufficient: answers must be generated and evaluated separately. Neither command invokes GPT.

Tests currently run on demand. Automated CI or cron schedules should only be introduced when the legal corpus updates periodically or team rhythm demands it.

## Reading Artifacts

`make check` creates `evals/runs/<UTC>-tests/` containing:

- `pytest.txt`: Human-readable output detailing failing test names and stack traces.
- `junit.xml`: Machine-readable results for CI tools and historical comparison.
- `tests.json`: Timestamp, command, status, exit code, Git commit and dirty status, code/test/config file hashes, and Python package versions.

The runner preserves the exit code of pytest: failed tests fail the command while persisting the report. If aborted prematurely, status may remain `running`; do not treat this as passed.

`make eval-retrieval` saves `retrieval.json` as before, enriched with version metadata, tracking top-k, score thresholds, dataset/corpus hashes, and index manifests against cached embeddings. Missing caches trigger offline errors.

Metadata uses an allowlist and never records `.env` or API key values. Code hashing catches uncommitted working directory edits; it does not replace Git revision control. Old reports without code hashes remain intact and are not backfilled.

## Core Takeaway

Passing logic tests confirms that current assertions hold true. Product response quality requires evaluation against authentic datasets and domain rubrics. For example, during the [deduplication improvement](runs/dedup-before-after.md), exact gold ID recall increased, but primary evidence completeness remained unchanged.
