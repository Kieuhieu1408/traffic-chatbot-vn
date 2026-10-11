# Level 2 — Logging Traces with LangSmith

**Goal:** Given an answer from the UI, inspect the query, history, actual retrieved sources, and generation output to pinpoint root causes of errors.

## Enabling & Usage

1. In LangSmith, generate an API key under Settings → API Keys. Set `LANGSMITH_API_KEY` in your local `.env`. Do not reuse OpenAI keys for this field.
2. Set `LANGSMITH_TRACING=true` and `LANGSMITH_PROJECT=rag-traffic-vn`. The default endpoint is US `https://api.smith.langchain.com`; if your workspace resides elsewhere, set the corresponding workspace endpoint. `LANGSMITH_WORKSPACE_ID` is only required when your key demands an explicit workspace ID.
3. Restart the API with `make serve` (terminate existing processes occupying port 8000 first).
4. Open the UI at `http://127.0.0.1:8000`, ask a question, and ask a follow-up question within the same session.
5. Open the `rag-traffic-vn` project in LangSmith and find `rag-traffic-chat`. Expand individual spans to cross-examine sources with the generated response. Turns sharing the same `session_id` are grouped into threads.

When enabled, queries, histories, retrieved passages, and generated answers are sent to the configured LangSmith project. Credential fields are never serialized into inputs or metadata. Set `LANGSMITH_TRACING=false` and restart to disable tracing.

## Trace Structure

- `rag-traffic-chat`: User query and session history preceding the current turn; outputs the answer, execution mode, and retrieved sources.
- `retrieve-sources`: Query, top_k, min_score; outputs chunk IDs, document/article metadata, raw text, similarity score, and rank. (Query rewriting based on history is not currently enabled for retrieval).
- `generate-answer`: System prompt, query, up to 3 history turns, retrieved sources, and model ID; outputs answer and mode. This step includes fallback logic, recorded as a chain without assuming an LLM API call always occurs.
- Metadata: `session_id`, model name, retrieval configuration, index manifest hash, and source code hash. The SDK records timestamps for each span.

Token usage and raw HTTP payloads are not currently tracked. If generation degrades to `evidence_only`, examine the mode and disclaimer in the response; not all completed turns represent successful RAG generation. Retrieval errors are recorded and surfaced to the API.

`/search` returns a `trace_id` for correlating requests. ID generation does not guarantee successful upload. `GET /health` reports `tracing_status`: `disabled`, `missing_api_key`, `configured`, `initialization_error`, or `upload_error`. `configured` verifies client configuration; trace visibility in LangSmith confirms actual cloud transport. Upload errors do not re-invoke models. The SDK batches records and flushes upon normal shutdown; abrupt termination may drop pending traces.

**Update:** Shiny reads LangSmith traces directly and saves `answer_pass` and `review_reason` back to the trace, while maintaining support for local JSONL files. See `review/README.md`. Eval runners do not forward traces to LangSmith; tracing focuses on UI/API `/search`. `make check` disables live tracing and uses mock clients for integration tests.

## Verification Status

Verified using the official SDK with mock transports: parent-child hierarchies, multi-turn history propagation, source content preservation, credential exclusion, disabled/missing key handling, retrieval failures, and upload errors. All 34 tests pass. Live `/search` calls on 2026-09-08 confirmed trace retrieval via LangSmith API: root and child spans completed with `rag` mode.

Official documentation: [Custom instrumentation](https://docs.langchain.com/langsmith/annotate-code), [Client configuration](https://docs.langchain.com/langsmith/trace-without-env-vars), [Threads](https://docs.langchain.com/langsmith/threads).

Sample verification trace: `01a07d06-517e-7633-9a21-17eddabcd128`. [Open in LangSmith](https://smith.langchain.com/o/2d8c44c4-6d13-4f24-83e2-dd189e50fc41/projects/p/1a9b8ad6-f915-429f-a9b0-a311549a0e86/r/01a07d06-517e-7633-9a21-17eddabcd128?poll=true).

## Verification with SmithDB API

Initial validation used legacy commands (`read_run`, `get_run_url`). These have been updated in the verification module to `await client.runs.retrieve(...)` and `await client.runs.get_url(...)` with explicit `project_id` and selectors:

```bash
.venv/bin/python -m evals.verify_langsmith \
  --project-id 1a9b8ad6-f915-429f-a9b0-a311549a0e86 \
  --run-id 01a07d06-517e-7633-9a21-17eddabcd128
```

Executed on 2026-09-08: successfully retrieved trace status and URL via the updated API without SDK deprecation warnings.
