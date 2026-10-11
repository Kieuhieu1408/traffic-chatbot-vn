# RAG Traffic VN · Data Review

Goal: inspect the conversation, compare the answer with retrieved evidence, and save a review without switching applications.

```bash
make review
```

Open http://127.0.0.1:8001. Interface text is English; original questions, answers, source documents, and existing review notes keep their original language. Reviewing does not call GPT or reload the embedding index.

## LangSmith workflow

The default source is the project configured by `LANGSMITH_PROJECT` in `.env`. The server uses `LANGSMITH_API_KEY`, endpoint and optional workspace ID; credentials stay server-side.

1. The queue loads up to 100 recent completed `rag-traffic-chat` root traces. Click **Refresh traces** to fetch new traces and feedback.
2. Use **Filter queue** for review status, single/multi-turn conversations, or question keywords.
3. Read **Conversation**, including expandable history. Click an answer citation to open and highlight the matching source in **Evidence the model saw**. History citations are not linked to the current turn's sources.
4. Choose **Pass** or **Fail** and enter a source-based reason for failures. Optionally enter a corrected answer.
5. **Save & next** saves and verifies the review, then advances. **Save without moving** keeps the current trace. **Skip** navigates without creating a label. Unsaved changes require an explicit choice before navigation or refresh.
6. **Open trace in LangSmith** opens the original root run. Mobile uses Conversation / Evidence / Review tabs.

The UI reads and writes `answer_pass` and `review_reason` on the original run. Pass=1 and Fail=0; existing category labels such as `Đạt ` and `Trượt ` are preserved in LangSmith. Optional corrected text is stored as `correction.answer` on `answer_pass`. It does not change the model's original answer. Existing feedback is updated instead of creating another rating on each save. Other feedback keys are untouched. When multiple records exist for one key, the latest is displayed and updated; older records remain.

A save records a human-review comment. Existing feedback can originate from a human or assistant; the queue counts both as reviewed and displays the available reviewer information. Counts are not human-judge agreement measurements. An explicit empty reason on Pass is allowed.

Refresh builds a complete snapshot before replacing the queue. Before a save, the adapter checks that feedback has not changed since it was loaded. After writing it reads back both fields. A failed/unverified save keeps the form and never advances. LangSmith uses two writes here, not a transaction: a partial write can occur. In that case copy any unsaved edits, discard and refresh to inspect the server state. The concurrency check is best-effort, not an atomic lock for simultaneous reviewers.

Run retrieval and links use the SmithDB SDK APIs. Feedback creation includes the project UUID as `session_id` and the run start time, avoiding the deprecated lookup path. No new paid model calls are made by load, refresh, export or save.

## Local eval compatibility

Choose **Local · …** to review a stored `evals/runs/*/answers.jsonl` batch. Existing SQLite labels remain in `evals/labels/human.sqlite3`; local saves preserve the optional legacy error-group field. Local gold evidence is shown only when dataset hashes match. Local labels are not automatically uploaded or combined with cloud feedback.

**Export reviews** exports the loaded cloud queue's reviews when LangSmith is selected, or the local label database when a local batch is selected. This is not a full-project archival export beyond the loaded 100 traces.

## Verification

- Live read: project and 10 completed traces loaded, existing feedback and trace links inspected.
- Adapter tests: create/update identity, SmithDB lookup keys, no duplicate feedback on resave, conflict detection, failed writes, source hash checks, optional Pass reason, and existing category mapping.
- Browser checks with isolated fake transport: required reason, unsaved navigation, Save & next, preserved run identity, reopening saved feedback, filters/empty state, mobile citation and layout. Real reviews were not edited by browser tests.
- The server remains bound to localhost. This is a personal review tool; no multi-user authentication is provided.

## Blind judge calibration

Completed local judge batches appear as **Blind review · …** sources. These use frozen trace inputs and the batch's rubric, not the editable cloud-review queue. Existing human/assistant feedback is never prefilled. Save your own review before explicitly revealing the judge; the first review is locked and stays separate from `answer_pass` / `review_reason`. The independence checkbox is off by default; do not check it for previously exposed cases. See [the judge guide](../evals/judge-guide.md) for metrics, abstentions, storage and limitations.
