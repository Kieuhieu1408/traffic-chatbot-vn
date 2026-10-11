# Level 3: IDP retrieval A/B pilot

Goal: learn whether normalization helps people resolve questions, beyond an offline retrieval score.

Status: instrumentation ready, disabled by default. No actual user experiment, measured uplift or winner yet.

## Hypothesis and variants

For queries explicitly naming an international driving permit in Vietnamese, expanding the name to the canonical term plus IDP will increase user-reported helpfulness.

A: previous retrieval, no alias expansion. B: alias expansion. Keep corpus/index, top-k, threshold, generation prompt and model identical. Model outputs can still vary. Record variant and effective retrieval query in LangSmith.

## Eligibility and assignment

Enable with `RAG_AB_ENABLED=true` before starting `python app.py`. The change applies only when alias normalization changes the query. Deterministic SHA-256 hashing of experiment ID and session ID splits sessions approximately 50/50. The UI generates a random session UUID. Repeated eligible questions in one session stay in the same arm. Clearing a session generates a new assignment; this is session randomization, not person randomization. API clients can supply IDs, so do not use untrusted automated traffic for a real study.

All non-eligible questions retain current behavior. The same interface asks both arms: “Did this answer help resolve your question?” Yes/No. Variant is not shown. Feedback is user_reported_helpfulness, not answer_pass or legal correctness. Automation and assistant test runs must use an isolated database, never count as user feedback.

## Measures fixed before user collection

Unit: first eligible answer per session, avoiding prolific sessions dominating results.

Primary descriptive measure: confirmed helpful first answers / eligible sessions. This measures confirmed helpfulness, not true task success. Always report response rate and helpfulness among respondents alongside it; no response is missing, not a No label. Differential response rates can bias comparisons.

Guardrails: latency p95 and evidence-only frequency. Follow-up count was an initial idea, but is not implemented or interpreted as failure: a follow-up can be a new question. Exceptions before a completed response are not recorded by this local store; monitor service errors separately before real rollout.

Read-only summary: `.venv/bin/python -m evals.ab_report`. Database defaults to `data/ab/events.sqlite3` (under configured index parent when custom index path is used); use `--db` for a custom path. Feedback updates the same exposure instead of adding votes. No raw questions/answers stored in this database; trace IDs link to LangSmith. Local response UUID acts as the feedback capability; this is local pilot infrastructure, not an authenticated public survey.

## Collection and stopping

First run a fixed 14-day feasibility pilot with volunteer users; include all eligible sessions within the window. Start/end dates must be recorded before enabling real collection. Do not stop early because one arm looks better. At the end, report sample counts, missingness and descriptive outcomes; low traffic means inconclusive, not “B wins”. No powered confirmatory test is claimed. Use observed baseline and a product-relevant minimum improvement to plan sample size for a later confirmatory trial.

Stop for a material service regression, but retain logs and report the reason. Roll back by disabling RAG_AB_ENABLED and restarting; normal behavior uses current B normalization. Do not change variants mid-experiment; assign a new experiment ID for future changes.

## Limits and completion

Technical readiness is not an A/B result. Real participants, launch dates and enough data are still absent. Human/domain evaluation remains needed for legal correctness. AI-generated questions and labels cannot replace user outcomes.
