# Company Policy Assistant

A production-oriented RAG knowledge assistant for company policy questions — grounded in an internal knowledge base only, with citations, and backed by real, measured retrieval and generation quality numbers rather than a demo you just have to trust.

Built for **Nexora Technologies**, a fictional company, as a portfolio project demonstrating eval-driven RAG engineering end to end: hybrid retrieval, reranking, grounded generation, and a benchmark that proves each stage's contribution.

## Why this exists

Most "RAG chatbot" projects show a demo and ask you to take their word for it. This one is built around the opposite premise: a corpus **deliberately engineered** to contain the failure modes real company knowledge bases actually have — conflicting policies (contractors vs. full-time), stale cross-references, ambiguous terminology, superseded document versions — and a 39-question benchmark that measures whether the pipeline actually handles them, before and after each retrieval stage.

## Measured results

From `eval/results/latest.md` (regenerate anytime with `uv run python scripts/eval.py`):

| Retrieval stage | Recall@5 | Recall@10 | MRR | nDCG@5 |
|---|---|---|---|---|
| Hybrid only (dense + BM25 + RRF) | 55.1% | 73.1% | 48.5% | 46.5% |
| **+ Reranking (cross-encoder)** | **81.0%** | **94.9%** | **71.7%** | **70.9%** |

Reranking alone lifts Recall@5 by ~26 points. Per-category numbers, and where reranking *doesn't* help, are in the full report.

**Generation quality** (LLM-judge, same model generating and judging — a directional signal, not an unbiased score): **92.3% faithful** (answers don't invent facts outside retrieved context), **82.1% correct** against reference answers. All 3 deliberately out-of-scope questions (e.g. "does the company offer stock options?") were correctly declined rather than hallucinated.

## Architecture

```
corpus/ (markdown + frontmatter)
        │
        ▼
Structure-aware chunking (section/subsection-aware, metadata-preserving)
        │
        ├──────────────┬──────────────┐
        ▼              ▼
  Dense embeddings   BM25 index
  (bge-small, CPU)   (rank_bm25)
        └──────┬───────┘
               ▼
     Hybrid retrieval (Reciprocal Rank Fusion)
               ▼
     Reranking (cross-encoder, CPU)
               ▼
     Grounded generation (LLMProvider: Groq / Gemini)
               ▼
     Answer + citations (from retrieved context, not model claims)
```

`FastAPI` backend (`POST /chat`, `GET /documents`) + a minimal `Next.js` chat frontend sit on top of the pipeline.

## Tech stack (free-tier only, by design)

| Component | Choice |
|---|---|
| Embeddings | `BAAI/bge-small-en-v1.5` via `sentence-transformers`, CPU |
| Sparse retrieval | `rank_bm25`, in-process |
| Vector store | FAISS (`IndexFlatIP`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2`, CPU |
| LLM generation | Groq or Gemini, behind a provider-agnostic `LLMProvider` interface — swappable via one env var, no pipeline code changes |
| Evaluation | Hand-rolled Recall@K/Precision@K/MRR/nDCG + a custom LLM-judge for faithfulness/correctness |
| Backend | FastAPI |
| Frontend | Next.js + Tailwind |

No paid APIs, no GPU dependency for serving — everything here runs on free tiers and CPU inference.

## Known limitations (measured, not hidden)

Honesty about what's still broken is part of the point of an eval-driven build:

- **Applicability-conflict queries** (e.g. "I'm a contractor, how many leave days do I get?") — the reranker sometimes ranks a generic policy chunk above the specific exclusion that actually answers the question. Root-caused, not yet fixed.
- **Paraphrased/indirect queries** — a question about "relaxing in Dubai next month" fails to retrieve the international remote-work policy, because BM25 confidently (and wrongly) matches on literal wording ("work remotely") rather than the implied meaning ("Dubai" → international). This needs query understanding/rewriting, not retrieval tuning — no reranker or fusion-parameter change fixes it.
- **Version-delta queries** sit at 60% recall regardless of reranking — the weakest category in the benchmark.

Each of these has a documented root-cause investigation, not just a symptom description. Next iteration targets these specifically, measured against the same benchmark before/after.

## Running it locally

```bash
# Backend
uv sync
cp .env.example .env   # add a free Groq or Gemini API key
uv run python scripts/build_vector_index.py
uv run python scripts/build_bm25_index.py
uv run python scripts/serve.py     # http://127.0.0.1:8000/docs

# Frontend
cd frontend
npm install
npm run dev                        # http://localhost:3000

# Evaluate
uv run python scripts/eval.py      # writes eval/results/latest.md
```

`scripts/chat.py` gives an interactive terminal view of retrieval + reranking + the generated answer together, useful for debugging without the frontend.

## Project structure

```
corpus/                  Policy documents (deliberately designed corpus, see corpus/README.md)
eval/                    Benchmark question set + eval results
src/company_policy_assistant/
  ingestion/              Parsing, structure-aware chunking
  retrieval/              Embeddings, FAISS, BM25, hybrid fusion, reranking
  generation/              LLMProvider abstraction, grounded-answer generation, citations
  evaluation/              Retrieval metrics, LLM-judge, benchmark resolution
  api/                    FastAPI app
scripts/                  CLI entry points (build indexes, chat, eval, serve)
frontend/                 Next.js chat UI
```
