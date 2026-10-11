# Business Requirements Document (BRD)
## Project: traffic-chatbot-vn — Vietnamese Traffic Law Retrieval Assistant

---

### 1. Problem Statement & Background

#### 1.1. Current State of Traffic Law Inquiries in Vietnam
The Vietnamese road traffic legal framework (including the Road Traffic Law, Government Decrees, Circulars from the Ministry of Transport / Ministry of Public Security, and National Technical Regulations - QCVN) exhibits distinct challenges:
- **Dispersed and Voluminous:** A single driving scenario (e.g., motorcycle speed limits, lane transitions, International Driving Permits) may be governed by multiple separate documents (Circular 31/2019/TT-BGTVT, Decree 100/2019/ND-CP, Circular 29/2015/TT-BGTVT, etc.).
- **Complex Legal Provisions & Detailed Matrices:** Many regulations are organized into multi-dimensional matrix tables (dual carriageway vs. two-way road, within vs. outside densely populated areas, car vs. truck vs. motorcycle categories). Citizens find it difficult to look up rules rapidly while on the road.
- **Heterogeneous Document Formats:** Actual stored documents exist in varied formats: Word (`.docx`, legacy `.doc`), native PDF, scanned PDF requiring Vietnamese OCR, and draft documents occasionally mixed with official enactments.

#### 1.2. Limitations of Generic Large Language Models (LLMs)
When utilizing generic LLMs (e.g., standard ChatGPT, Gemini, Claude) for Vietnamese traffic inquiries, users face severe hazards:
- **Legal Hallucinations:** Models invent arbitrary fine amounts, confuse maximum permissible speeds between divided and undivided roads, or fabricate non-existent legal identifiers.
- **Lack of Factual Grounding:** Answers remain vague without citing specific Articles, Clauses, or statutory numbers.
- **Real-World Legal Liability:** If drivers rely on inaccurate AI advice, they risk committing violations, incurring fines, having licenses revoked, or causing traffic hazards.

#### 1.3. The Solution: traffic-chatbot-vn
The **traffic-chatbot-vn** project provides **an automated, accurate question-answering system for Vietnamese road traffic laws leveraging Retrieval-Augmented Generation (RAG) combined with strict quality guardrails and observability.**

The core imperatives are:
1. **Factually Grounded:** Every statement must be backed by authenticated statutory documents.
2. **Transparently Cited:** Every legal assertion must include verifiable citations down to the Article/Clause level.
3. **Scope-Aware:** The system operates strictly within known boundaries: no guessing, no hallucination, and explicit disclosure of corpus status.

---

### 2. Project Objectives & KPIs

#### 2.1. Business Objectives
- Deliver a reliable, user-friendly natural language traffic law assistant for drivers and citizens.
- Reduce research time for driving instructors, legal specialists, and vehicle operators.
- Establish a standardized workflow spanning data ingestion, normalization, indexing, automated evaluation, and human-in-the-loop review.

#### 2.2. Success Metrics & KPIs
System quality is measured against a **4-pillar evaluation rubric**:
1. **Prompt Compliance:** Directly addresses the specific vehicle, road type, action, and question context.
2. **Factual Grounding & Citation:** Every assertion includes citations (`[n]`) referencing retrieved passages; cited sources must genuinely support the claim.
3. **Completeness:** Core prerequisites or exceptions that alter conclusions must not be omitted.
4. **Scope & Humility:** No extrapolation regarding legal validity when data is incomplete; never equates "missing from retrieved context" with "legally prohibited".

**Technical KPIs:**
- **Zero Hallucination:** 0% critical factual errors regarding core safety and penalty regulations.
- **Citation Precision:** 100% of citation tokens `[n]` must correspond to relevant documents in top retrieved candidates.
- **Graceful Fallback:** 100% of LLM failures or unconfigured API keys must degrade to `evidence_only` mode (returning original verified snippets) rather than crashing or inventing content.

---

### 3. User Personas & Use Cases

| Persona | Core Need | Key Challenge | Value Provided |
| :--- | :--- | :--- | :--- |
| **Vehicle Operators (Drivers, Commuters)** | Quickly check speed limits, lane usage rules, International Driving Permits (IDP). | Unfamiliar with legal document numbers; often confuses divided vs. undivided road rules. | Clear, concise answers stating exact conditions (e.g., inside vs. outside populated areas) with statutory citations. |
| **Driving Instructors / Legal Specialists** | Locate official statutory references for lecture materials or student queries. | Time-consuming to search across hundreds of PDF/Word pages. | Pinpoint retrieval of Articles/Clauses with source file paths and raw text for verification. |
| **AI Engineers / Reviewers (Internal)** | Assess system quality; detect retrieval misses or ungrounded responses. | Difficult to audit RAG traces and annotate human labels at scale. | Interactive Review UI (Shiny), end-to-end tracing (LangSmith), and automated LLM-as-a-Judge pipeline. |

---

### 4. Project Scope

#### 4.1. In-Scope
- **Multi-Format Document Processing:**
  - Ingests `.docx`, legacy `.doc`, and `.pdf` files (including scanned PDFs with Vietnamese Tesseract OCR).
  - Automatically identifies and excludes "Draft" documents from the default search index.
  - Extracts metadata (document number, issuance date, issuing authority, title).
  - Segments documents by Article structure while preserving inline tables.
- **RAG Pipeline:**
  - Lightweight, effective multilingual embedding model (`intfloat/multilingual-e5-small`).
  - Vector indexing and similarity search via FAISS (`IndexFlatIP`).
  - Answer synthesis with source attribution via OpenAI Chat Completions API.
  - Safe fallback mode (`evidence_only`) when LLM is unavailable.
- **Multi-Turn Session Management:**
  - Secure conversational history tracked by `session_id` with LRU memory eviction.
- **Monitoring, Evaluation & Experimentation:**
  - Direct REST-based LangSmith tracing (lightweight, framework-agnostic).
  - A/B testing module for query expansion evaluation.
  - Interactive Human Review UI built with Shiny for Python.
  - LLM-as-a-Judge automation based on the standard evaluation rubric.

#### 4.2. Out-of-Scope
- **Real-Time Statutory Validity Tracking:** Operates on pre-ingested offline corpora; does not crawl live government databases or certify present-day legal validity (clear disclaimers are presented to users).
- **Formal Legal Representation:** Serves as an informational inquiry tool, not a replacement for certified legal counsel in litigation.

---

### 5. Functional Requirements

1. **FR-01: Natural Language Inquiry:**
   - Accepts natural language queries and responds with clear, coherent Vietnamese explanations.
2. **FR-02: Mandatory Citations:**
   - Every legal conclusion is tagged with `[1]`, `[2]`, mapped directly to listed source references.
3. **FR-03: Transparent Evidence Display:**
   - Displays retrieved snippets including: Document number, Document title, Article/Clause, source file path, and cosine similarity score.
4. **FR-04: Multi-Turn Conversation Context:**
   - Resolves follow-up questions (e.g., "What about motorcycles?") utilizing up to 3 previous conversation turns within the session.
5. **FR-05: Safe Fallback (Evidence-Only Mode):**
   - Automatically degrades to returning top retrieved raw statutory passages when `OPENAI_API_KEY` is absent or the API fails.
6. **FR-06: User Feedback:**
   - Provides Helpful / Unhelpful rating buttons to collect user feedback for continuous improvement.
7. **FR-07: Execution Tracing & Observability:**
   - Logs queries, retrieved chunks, generated answers, and latencies into tracing backends for debugging and auditing.
8. **FR-08: Human Review Interface:**
   - Delivers a dedicated reviewer interface to audit conversations, compare against evidence, record Pass/Fail decisions with structured rationales, and submit gold answers.

---

### 6. Non-Functional Requirements

- **Reliability & Safety:**
  - Zero leakage of secrets (API keys, tokens) in source code, logs, or UI responses.
  - Strict scope awareness to prevent speculative answers beyond provided text.
- **Performance & Efficiency:**
  - Embedding and FAISS search operate smoothly on CPU without requiring GPU acceleration.
  - Retrieval latency < 200ms across thousands of chunks.
- **Data Integrity:**
  - Enforces SHA-256 hash validation for index artifacts and metadata via `manifest.json`. Rejects mismatched or corrupt indexes at startup.
- **Maintainability & Modularity:**
  - Decoupled modules (`rag_traffic/ingest.py`, `indexing.py`, `retriever.py`, `generation.py`), strict typing hints, and offline-executable unit tests.

---

### 7. Risk Analysis & Mitigations

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Outdated or amended legal provisions** | Critical | Prominent disclaimer display; system does not speculate on validity; exact issuance dates and document numbers preserved in chunk metadata. |
| **Duplicate content between PDF and DOCX files** | Medium | Two-tier deduplication: Tier 1 deduplicates identical SHA-256 content hashes at ingestion; Tier 2 performs dynamic content deduping during retrieval (4x candidate pooling). |
| **Parsing errors in complex speed/penalty tables** | High | Leverages `iter_inner_content()` in `python-docx` to preserve inline tables in sequential order directly under parent Articles. |
| **LLM API outage or token exhaustion** | Medium | Automatic graceful degradation to `evidence_only_answer`, ensuring users still receive authentic source passages. |
| **Faulty negative extrapolation (Exclusivity Error)** | High | Employs Rubric v3 LLM-as-a-Judge with explicit exclusivity checks and claim-level verification before promotion. |
