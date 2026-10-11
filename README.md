# traffic-chatbot-vn

A reproducible baseline RAG system for querying Vietnamese traffic law documents. The system extracts text from PDF, DOC, and DOCX files, segments content by articles/sections, generates embeddings using `intfloat/multilingual-e5-small`, performs cosine similarity search via FAISS, and provides cited sources for each passage.

> **Disclaimer:** Data is currently restored from a March 2025 archive. There is no comprehensive audit of the validity status, amendments, or repeals of these documents yet. Results are intended for reference only and must be verified against official legal sources.

Internal checks currently do not find `168/2024/NĐ-CP` or `36/2024/QH15` in the corpus. This is an acknowledged data gap, not a retrieval defect.

## Changes Compared to the Prototype

- Source data, generated indexes, and archives are decoupled from source code and ignored by Git.
- Each chunk has a unique ID and SHA-256 hash; exact duplicates are deduplicated during ingestion.
- Files containing "Dự thảo" (Draft) in their name are excluded from the default index and recorded in the ingestion report.
- FAISS applies cosine similarity properly: embeddings are normalized and queried using `IndexFlatIP`.
- `manifest.json` tracks model name, vector dimensions, chunk count, and metadata hashes. The API rejects mismatched indexes.
- The API starts reliably and reports `/health` status clearly even if the index has not been generated yet.
- Conversation history is partitioned by `session_id` with memory limits instead of using a global shared variable.
- No API keys in code. When LLM is unconfigured, the system operates in `evidence_only` mode.
- Frontend displays structured sources safely without rendering LLM-generated raw HTML.

## Project Structure

```text
rag_traffic/                 # Ingestion, indexing, retrieval, and generation
tests/                       # Offline unit tests
static/index.html            # Web interface
data/raw/Thongtu/            # Extracted data (not committed)
data/index/                  # Chunks + FAISS index + manifest (reproducible)
data/legacy/                 # Old metadata/index for reference
data/archives/               # Original ZIPs; contains historical secrets, not committed
metadata.py                  # Ingestion CLI
embeddings.py                # Index building CLI
retrieval.py                 # Retrieval CLI
app.py                       # FastAPI application
```

## Installation

We recommend using `uv` and PyTorch CPU to avoid downloading unnecessary CUDA packages:

```bash
make install
```

Or install manually:

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python torch \
  --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/bin/python -r requirements.txt
```

To enable OCR for scanned PDFs on Ubuntu/Debian:

```bash
sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-vie
```

If Tesseract is not installed, ingestion still completes for readable documents and logs errors to `data/index/ingestion-report.json`.

Without `sudo` privileges, the pipeline also automatically recognizes user-local installations at `~/.local/opt/tesseract`. You can override the location via `RAG_TESSERACT_ROOT` or point directly to the binary using `RAG_TESSERACT_CMD`.

## Data Processing & Indexing

```bash
make ingest
make index
```

Generated artifacts:

```text
data/index/chunks.jsonl
data/index/ingestion-report.json
data/index/faiss.index
data/index/manifest.json
```

The [E5 model card](https://huggingface.co/intfloat/multilingual-e5-small) requires `passage:` and `query:` prefixes for retrieval tasks, including non-English languages. The pipeline automatically prepends these prefixes. FAISS uses `IndexFlatIP` on normalized vectors so the inner product equals cosine similarity, per [FAISS documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes).

## Running the Application

Test retrieval via CLI:

```bash
.venv/bin/python retrieval.py "Quy định về tốc độ tối đa của xe máy?"
```

Run Web / API:

```bash
make serve
```

Open `http://127.0.0.1:8000`. Check health status at `GET /health` and OpenAPI documentation at `/docs`.

### Enabling Answer Generation

Create `.env` from `.env.example` if not already present, then provide your OpenAI API key:

```dotenv
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.4-mini
```

The application calls the OpenAI Chat Completions API directly. Default model is `gpt-5.4-mini`, configurable via `OPENAI_MODEL`. When `OPENAI_API_KEY` is not set, the `/search` endpoint remains operational but returns only evidence snippets. Restart the server after modifying `.env`.

## Testing

```bash
make test
```

Unit tests do not invoke LLMs. Before production use, a gold benchmark dataset of questions, verified answers, and statutory articles should be added to measure Recall@k, MRR, and citation precision.

## Data Security & Hygiene

- Never commit `data/`, ZIP files, or `.env` to a public repository.
- Restored `src-*.zip` archives contain a historical OpenRouter key. That key must be revoked, and source code must not be extracted directly into the repository.
- The corpus currently includes drafts and multiple PDF/DOCX versions of the same documents. Legal validity cannot be inferred solely from timestamps or filenames.

## Review Traces in Shiny

```bash
make review-install
make review
```

Open `http://127.0.0.1:8001`. The English interface loads the configured LangSmith project, shows conversation history and retrieved sources, and writes `answer_pass` / `review_reason` to the original trace. Corrected answers are optional. Use **Save & next** for the normal review flow. Reviewing does not call GPT.

Local eval batches and existing SQLite labels are still available from **Data source**. See [review/README.md](review/README.md) for refresh, filtering, export and save behavior.

## Verification After Changes

Run `make check` to run tests and persist results paired with code/test hashes in `evals/runs/<UTC>-tests/`. When modifying retrieval logic, also run `make eval-retrieval` to benchmark the 10-query test set against cached embeddings. Neither command calls GPT. See [Workflow and Reporting](evals/regular-checks.md).

## LangSmith Tracing for UI/API

Set `LANGSMITH_API_KEY` in `.env`, enable `LANGSMITH_TRACING=true`, and restart `make serve`. Every `/search` request logs a `rag-traffic-chat` trace with retrieval and generation steps in the `rag-traffic-vn` project. Questions, history, sources, and answers are forwarded to this project without requiring LangChain.

See [LangSmith Tracing Guide](evals/langsmith-tracing.md). `/health` reports configuration status; trace uploads are confirmed only when visible in LangSmith. Shiny reads LangSmith traces directly and saves feedback back to the trace, while maintaining support for local runs.

## Judge Pilot and Blind Review

`make judge` explicitly runs a paid, bounded judge pilot on 10 existing traces without regenerating answers. Completed batches appear in Shiny as **Blind review** sources. Judge results and first human labels stay separate from LangSmith review feedback. See [evals/judge-guide.md](evals/judge-guide.md); the current pilot is not yet calibrated against independent human labels.
