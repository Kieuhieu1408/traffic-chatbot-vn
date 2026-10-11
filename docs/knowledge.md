# Technical Knowledge Base
## Comprehensive Guide to Core Concepts, Theory & Engineering Decisions in traffic-chatbot-vn

This document details foundational and advanced engineering principles implemented in the project, enabling any software or AI engineer to understand every architectural decision and replicate the system from scratch.

---

### TABLE OF CONTENTS
1. [Core Concepts of Retrieval-Augmented Generation (RAG)](#1-core-concepts-of-retrieval-augmented-generation-rag)
2. [Document Parsing & Legal Data Processing](#2-document-parsing--legal-data-processing)
3. [Text Embeddings & Vector Search (FAISS)](#3-text-embeddings--vector-search-faiss)
4. [Prompt Engineering & Hallucination Mitigation](#4-prompt-engineering--hallucination-mitigation)
5. [Backend Architecture & Session State Management](#5-backend-architecture--session-state-management)
6. [LLMOps, Observability & Evaluation](#6-llmops-observability--evaluation)
7. [Advanced Model Adaptation (PEFT & QLoRA)](#7-advanced-model-adaptation-peft--qlora)

---

### 1. Core Concepts of Retrieval-Augmented Generation (RAG)

#### 1.1. Why Pure LLMs Fail in Legal Jurisdictions
Large Language Models (such as GPT-4, LLaMA, Qwen) store knowledge in parametric memory (neural network weights). In statutory domains, this introduces severe failure modes:
- **Knowledge Cutoff:** Models cannot know statutes, circulars, or decrees enacted after their training cutoff date.
- **Critical Hallucinations:** When prompted for a statutory clause, LLMs generate statistically fluent word sequences rather than factually verified statements. Consequently, models fabricate penalty amounts, confuse speed thresholds, or cite fictitious document numbers.
- **Lack of Auditability:** Organizations and citizens cannot trace an answer back to its exact statutory source, page, or clause.

#### 1.2. How RAG Solves Parametric Blind Spots
RAG resolves these limitations by marrying:
1. **Non-parametric Memory:** An external corpus of authoritative legal documents indexed as discrete text chunks and vector embeddings.
2. **Retrieval:** Upon receiving a query, semantic similarity search extracts the most relevant passages from non-parametric storage.
3. **Augmentation:** The user query and retrieved statutory passages are packed into a grounded prompt.
4. **Generation:** The LLM functions strictly as a reading comprehension engine: synthesizing the provided evidence into an answer with transparent citations.

#### 1.3. Naive RAG vs. Production RAG
- **Naive RAG:** Naively splits text into arbitrary token sizes (e.g., 500 characters), applies standard embeddings, retrieves top-k passages, and feeds them into generic prompts. Consequences: Tables are cut in half, citations point to wrong articles, and models hallucinate when context is incomplete.
- **Production RAG (as built in traffic-chatbot-vn):**
  - Hierarchical statutory chunking preserving Articles and Clauses.
  - End-to-end deduplication across file formats.
  - Unit-length normalized vectors with manifest integrity checksums.
  - Candidate over-fetching combined with runtime deduplication.
  - Graceful fallback (`evidence_only` mode) during external API degradation.
  - Full-lifecycle tracing and claim-level automated LLM-as-a-Judge audits.

---

### 2. Document Parsing & Legal Data Processing

#### 2.1. Multi-Format Administrative Document Challenges (.docx, .doc, .pdf)
- **Word Document Structure (`.docx`):** Word files store both paragraphs and tables. Invoking `doc.paragraphs` followed by `doc.tables` separates regulatory speed and penalty tables from their parent Article headings ("Article 6. Maximum permissible speeds").
  - *Engineering Solution:* Traverse blocks using `iter_inner_content()` in `python-docx` to preserve sequential document flow from top to bottom.
- **Scanned PDFs & OCR (Optical Character Recognition):**
  - Native digital PDFs: Processed via `pdfminer.six` directly.
  - Scanned images: Text extracted by `pdfminer` drops to near-zero characters.
  - *OCR Fallback Pipeline:*
    1. If extracted character count `< 200`, trigger OCR fallback.
    2. Render PDF pages via `pdf2image` (Poppler) at 250 DPI (optimal resolution for accented Vietnamese characters).
    3. Execute `pytesseract` with the `tesseract-ocr-vie` language pack.

#### 2.2. Vietnamese Unicode Normalization
Vietnamese characters exist under two distinct Unicode normalization forms:
- **NFC (Canonical Composition):** Accented characters stored as a single code point (e.g., `ệ` = `U+1EC7`).
- **NFD (Canonical Decomposition):** Accented characters stored as a base letter plus detached accent markers (e.g., `e` + `^` + `.` = `U+0065` + `U+0302` + `U+0323`).
Without canonical normalization (`unicodedata.normalize("NFC", text)`), identical text fails equality tests, corrupting searches and SHA-256 deduplication hashes. Processing also strips null bytes (`\x00`) and collapses erratic whitespace.

#### 2.3. Chunking Strategies
- **Why Avoid Fixed Token Splitting:** Severing a statutory article mid-sentence strips critical exceptions or vehicle applicability categories.
- **Structural Chunking:**
  - Primary boundary split on `Điều \d+`: Each chunk encapsulates a complete statutory Article.
  - **Sub-chunking with Overlap:** If an Article exceeds `max_chars = 1800` (e.g., extensive speed schedules), a sliding window splits it with 180-character overlap, anchored to line breaks (`\n`) or full stops (`. `).

#### 2.4. Content Hashing Deduplication
Corpora often contain identical regulations across drafts, scans, and Word versions:
$$\text{Content Hash} = \text{SHA256}(\text{lowercase}(\text{collapse\_whitespace}(\text{NFC\_normalize}(\text{text}))))$$
By tracking `seen_content`, redundant passages are removed at ingestion, preserving vector index capacity and search performance.

---

### 3. Text Embeddings & Vector Search (FAISS)

#### 3.1. Bi-Encoder vs. Cross-Encoder Architectures
- **Cross-Encoder:** Jointly encodes Query and Document through Transformer attention layers. Highly accurate but scales with \(O(N)\) per query across \(N\) documents. Computationally unfeasible at scale.
- **Bi-Encoder:** Independently projects queries to vector \(\mathbf{q}\) and documents to vectors \(\mathbf{d}\). Document vectors are pre-computed offline. At query time, only \(\mathbf{q}\) is embedded, allowing geometric similarity searches in milliseconds.

#### 3.2. E5 Model Architecture (`multilingual-e5-small`)
- Pre-trained on diverse multilingual contrastive pairs.
- **Asymmetric Task Prefixes:**
  - Information retrieval is asymmetric: queries are brief, while target passages are verbose and descriptive.
  - E5 mandates specific prefixes:
    - Passages: `"passage: "`
    - Search queries: `"query: "`
  - Omitting these prefixes causes vector space distortion, substantially lowering Recall and MRR.

#### 3.3. Mathematical Equivalence: Cosine Similarity & Inner Product
Cosine similarity between \(\mathbf{u}, \mathbf{v} \in \mathbb{R}^d\):
$$\text{Cosine}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^d u_i v_i}{\sqrt{\sum_{i=1}^d u_i^2} \sqrt{\sum_{i=1}^d v_i^2}}$$

Applying **L2 unit-length normalization** at embedding generation:
$$\hat{\mathbf{u}} = \frac{\mathbf{u}}{\|\mathbf{u}\|_2} \implies \|\hat{\mathbf{u}}\|_2 = 1$$
Yields direct equality:
$$\text{Cosine}(\hat{\mathbf{u}}, \hat{\mathbf{v}}) = \hat{\mathbf{u}} \cdot \hat{\mathbf{v}} = \langle \hat{\mathbf{u}}, \hat{\mathbf{v}} \rangle = \text{Inner Product}$$

**Performance Implication:** Inner products require only multiply-accumulate operations (vectorized via SIMD/AVX on CPU), eliminating square roots and divisions during search.

#### 3.4. FAISS (Facebook AI Similarity Search)
- `IndexFlatIP`: Exact exhaustive search across all vectors. Across datasets of thousands to tens of thousands of chunks, `IndexFlatIP` delivers sub-10ms response times on CPU without the precision loss of approximate index structures (IVF/HNSW).

---

### 4. Prompt Engineering & Hallucination Mitigation

#### 4.1. In-Context Grounding Schema
Context provided to LLMs is structured systematically for precise attribution:
```text
[1] Document: 31/2019/TT-BGTVT
Title: Circular on speed limits and safe distance...
Article/Section: Article 6. Maximum permissible speeds for motor vehicles...
Source file: Thongtu/TT.31.2019.TT.BGTVT.docx
Content: <Verbatim statutory excerpt>
```

#### 4.2. Citation Enforcement & Validation
- System Prompt requirement: *"Every legal assertion must have citations such as [1], [2]."*
- Post-processing regex `re.findall(r'\[(\d+)\]', answer)` validates cited numbers against retrieved context. Hallucinated references beyond available ranks are flagged under `invalid_citation_ranks`.

#### 4.3. Exclusivity Fallacy Mitigation
- **The Issue:** When context states: *"Drivers holding IDPs issued by Vienna Convention member states must carry both their IDP and national license"*, models frequently leap to false negative inferences: *"All non-Vienna Convention nations reject IDPs"*.
- **Mitigation:** The system prompt and evaluation rubrics enforce: *"A source describing provisions within scope X does not implicitly deny cases outside scope X. Never assert mutual exclusivity unless explicitly stated."*

#### 4.4. Graceful Degradation (`evidence_only` Mode)
Production systems must not return empty 500 errors during upstream model interruptions:
- If API keys are unconfigured, or calls fail (rate limits, timeouts), `evidence_only_answer` returns the top 3 verified source passages directly with explicit disclaimers.

---

### 5. Backend Architecture & Session State Management

#### 5.1. Asynchronous Execution in FastAPI: I/O-Bound vs. CPU-Bound
- Upstream LLM calls and LangSmith logging are **I/O-bound** (waiting on network responses).
- Embedding calculations via SentenceTransformers and FAISS vector searches are **CPU-bound** (matrix operations).
- Running CPU-bound tasks directly inside an `async def` function blocks Python's single-threaded event loop.
- **Solution:** Wrap CPU-bound tasks in `fastapi.concurrency.run_in_threadpool`, delegating intensive computation to separate worker threads.

#### 5.2. Thread-Safe Session Store & Memory Management
- Backed by `OrderedDict` with `threading.Lock`:
  - **Thread-Safety:** Prevents race conditions during concurrent requests.
  - **LRU Cache Eviction:** Evicts least-recently-used sessions when exceeding `max_sessions = 500` (`popitem(last=False)`), preventing memory leaks.
  - **Sliding History Window:** Limits session history to `max_turns = 6` and injects only the 3 most recent turns into generation prompts to control token budget.

#### 5.3. Preventing Data & Model Drift via Manifest
- Changes in source documents or embedding models can silently desynchronize vector indexes from metadata stores.
- `manifest.json` locks: `chunks_sha256`, model identifier, dimensions, and chunk count.
- At startup, `VectorRetriever` executes pre-flight sanity checks, refusing to boot if discrepancies are detected.

---

### 6. LLMOps, Observability & Evaluation

#### 6.1. Tracing & Observability
- **Trace:** Represents the end-to-end lifecycle of a query.
- **Span:** Discrete pipeline stages within a trace (`retrieve-sources`, `generate-answer`).
- Lightweight implementation: Directly utilizes `langsmith.Client` via REST without loading heavy framework layers. Source code hashes (`retriever.py`, `generation.py`) are captured in trace metadata for exact reproducibility.

#### 6.2. Deterministic A/B Testing
- Evaluates query expansion variants without session volatility:
  $$\text{Variant} = \begin{cases} A, & \text{if first byte of SHA256}(\text{Experiment} + \text{SessionID}) < 128 \\ B, & \text{otherwise} \end{cases}$$
- Guarantees consistent user experiences within any ongoing session.

#### 6.3. Automated LLM-as-a-Judge
- Overcomes the failure of lexical metrics (BLEU/ROUGE) in legal verification.
- **Claim-Level Deconstruction:** Breaks answers into standalone claims and validates each claim against ground-truth evidence, categorizing issues into: `unsupported`, `citation`, `missing_condition`, `wrong_answer`, `scope`.

#### 6.4. Human-in-the-Loop Review
- Dedicated web portal built with Shiny for Python (`../review/app.py`).
- Reviewers audit production traces, inspect highlighted citations, record Pass/Fail determinations, and contribute curated gold answers for future retraining.

---

### 7. Advanced Model Adaptation (PEFT & QLoRA)

#### 7.1. When to Fine-Tune in RAG Architectures
RAG delivers relevant domain knowledge. However, to deploy a lightweight local open-source model (such as `Qwen3-1.7B`) on private hardware without commercial API reliance, fine-tuning aligns the model to rigorous legal citation structures without requiring verbose prompt instructions.

#### 7.2. QLoRA (Quantized Low-Rank Adaptation)
- **4-Bit NormalFloat Quantization (NF4):** Compresses base model weights from 16-bit to 4-bit, dropping VRAM footprints from tens of gigabytes down to 2-3 GB.
- **Low-Rank Adaptation (LoRA):** Freezes base weights \(W \in \mathbb{R}^{d \times k}\) and trains low-rank adapters \(A \in \mathbb{R}^{d \times r}\) and \(B \in \mathbb{R}^{r \times k}\) with rank \(r \ll \min(d, k)\) (e.g. \(r = 8\)):
  $$W_{\text{new}} = W + \frac{\alpha}{r} (A \cdot B)$$
- **Targeted Masked Loss:** Calculates Cross-Entropy loss exclusively on assistant response tokens, ignoring query prompts and context passages.

#### 7.3. Disjoint Document Splitting
In legal evaluation, questions from the same circular must not bleed across training and evaluation splits:
- **Disjoint Partitioning:**
  - Training Set: Exclusively Circular `12/2017`.
  - Development Set: Exclusively Circular `29/2015`.
  - Test Set: Exclusively Circular `31/2019`.
Ensures that test performance evaluates genuine statutory reading comprehension rather than memorization of familiar texts.
