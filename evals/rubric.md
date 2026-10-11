# RAG Answer Grading Rubric — v3

## Scope

Evaluates full answers against the question, conversational history, and retrieved evidence of each test case. Does not solely grade the primary gist. For `corpus-seed-10`, the scope is the textual version specified in the question, not real-time statutory validation.

Agreed standard: every assertion meaningful to the user must be factually accurate and grounded in evidence. Do not fail an answer solely for unpolished prose.

## Binary Decision

**Pass** requires satisfying all four criteria simultaneously:

1. **Intent Compliance:** Accurate vehicle, action, situation, and question scope.
2. **Grounded Claims:** Assertions are supported by retrieved context; cited sources genuinely back the stated point. System observations must stay within observable data.
3. **Completeness:** Does not omit statutory prerequisites or exceptions that alter conclusions.
4. **Scope & Humility:** No guessing when context is insufficient; no speculative validity claims; distinguishes retrieved context from the entire corpus.

**Fail** if there is at least one violation impairing meaning or reliability. A correct primary conclusion does not compensate for a secondary false or ungrounded claim that impacts the user.

**Unjudged** is a status, not a verdict. If the evaluator lacks sufficient basis or domain certainty, skip for review; never force an ungrounded Pass or Fail.

## Agreed Reference Example: Case 001

- The primary conclusion regarding roads separated only by paint markings is grounded in evidence.
- The assertion that "the corpus has not provided the complete text of the article" improperly generalizes from retrieved snippets to the overall corpus, without proof about corpus contents.
- Verdict: **Fail** under rubric v1 due to a Scope & Humility violation.
- Rationale: "Primary conclusion is correct, but the model generalized from missing context to a missing corpus."

Better phrasing: "The provided passages do not contain the full text of the article", if accurate regarding the actual retrieved context.

## Distinguishing System Defects from Answer Defects

- Chunks truncated at headings or the correct evidence ranking 4th indicate ingestion/retrieval signals to investigate. These do not automatically fail an answer if the generated content is complete, correct, and grounded.
- Retrieval missing sources where the model responds with appropriate humility regarding missing evidence can Pass on generation behavior; retrieval evaluation remains a separate task. Clearly indicate what component is being judged.
- The existence of citation tokens `[n]` does not prove the cited snippet supports the claim.

## Rationale Formatting

When marking **Fail**, state the faulty/missing claim, reference evidence, and violated criterion. For **Pass**, a rationale is optional. Error taxonomy and corrected gold answers are optional enrichment fields.

## Versions & Historical Labels

Rubric v1 replaced preliminary evaluations that focused only on the main idea. Historical labels and reports are not retroactively modified and require review when comparing under v1. Do not merge evaluations across differing rubric standards into a single metric.

## Clarifications v2 — 2026-09-08

**Goal:** Penalize errors that distort operational meaning without penalizing paraphrased expressions or demanding verbatim legal transcription.

- Permits reasonable inferences from context and plain meaning. Verbatim transcription of sources is not required. Never invent numbers, permissions, exceptions, or unprovable conditions.
- Evaluate conditions across the entire response and user scenario. "Must carry A and B" is a necessary condition; it does not automatically claim "carrying only A and B guarantees permission". Omitting peripheral details is a defect only if it flips the conclusion or misguides the user in the scenario.
- If an answer asserts eligibility/permission while omitting a condition that could alter the conclusion, mark **Fail**. If inconclusive from evidence, leave **Unjudged**.
- Facts supplied by user history can be adopted for the scenario. Historical assistant turns do not constitute authoritative legal sources.

### Adjudication of Two Development Cases (Assistant Labels, Non-Gold)

1. Motorcycle 60/70: **Pass**. The speed table is cited accurately; conditional response acknowledging the lack of dual-carriageway definitions is appropriate behavior. Signage placement provisions support the common-sense reading that specific speed limit signs govern speed; no penalty for omitting verbatim obligation phrasing. Retrieval still needs refinement to fully resolve roadway categorization.
2. IDP Use in Vietnam: **Pass**. The conclusion that Vietnamese IDPs are invalid in Vietnam is accurate. The foreign IDP section states both documents must be carried without asserting this is unconditionally sufficient. The Vienna Convention scope was stated upfront. Stating "only these two documents, regardless of vehicle class" would be a Fail.

These are operational learning decisions, subject to expert adjudication. Rubric v1 labels and prior judge runs remain preserved separately.

## Clarifications v3 — Exclusivity Fallacy

**Goal:** Detect assertions overstepping evidence without crude keyword matching.

A source describing rules within scope X does not implicitly deny cases outside scope X. Check whether the source states exclusive limits, exhaustive lists, or equivalent exclusivity clauses. Otherwise, asserting "only X", "strictly prohibited outside X", or equivalent statements is an ungrounded scope violation.

- A source requiring both IDP and national license when driving in Vienna Convention countries specifies obligations for member states; it does not prove non-member countries strictly reject IDPs.
- The word "only" is not automatically defective: "not exceeding 3 years" supports "a maximum of only 3 years", if the national license duration dependency is maintained.
- Statements without "only" can still be defective: "all countries outside the group reject IDPs" is also an invalid exclusivity claim.
- Evaluate the entire sentence: "The document only describes X, which is insufficient to determine Y" expresses scope limitation, not a prohibition of Y.

Example labels proposed by assistant for engineering development; not certified current law or expert gold. Historical v2 labels are preserved for baseline tracking.
