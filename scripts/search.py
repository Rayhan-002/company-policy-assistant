"""Compare hybrid-only vs. reranked retrieval against the corpus's deliberate test cases.

Usage: uv run python scripts/search.py "your query here"
"""

import sys
from pathlib import Path

from company_policy_assistant.ingestion import build_chunks
from company_policy_assistant.retrieval import BM25Index, HybridRetriever, Retriever, VectorIndex

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

TEST_QUERIES = [
    "I'm a contractor, how many annual leave days do I get?",
    "Can I work remotely from another country?",
    "What is the maximum travel reimbursement?",
    "What approval is required for a laptop purchase?",
    "How do I request leave due to illness?",
    "How do I get remote access to internal systems?",
    "What are the password requirements?",
]


def describe(chunk) -> str:
    section = " / ".join(filter(None, [chunk.section_name, chunk.subsection_name])) or "(preamble)"
    return f"{chunk.title} v{chunk.version} ({chunk.status}) - {section}"


def main() -> None:
    chunks = build_chunks()
    chunk_by_id = {c.chunk_id: c for c in chunks}

    vector_index = VectorIndex.load(DATA_DIR / "index")
    bm25_index = BM25Index.load(DATA_DIR / "index")
    hybrid = HybridRetriever(vector_index, bm25_index)
    retriever = Retriever(chunks, vector_index, bm25_index)

    queries = sys.argv[1:] if len(sys.argv) > 1 else TEST_QUERIES

    for query in queries:
        print(f"\n=== {query} ===")

        print("  -- hybrid only --")
        for chunk_id, score in hybrid.search(query, top_k=5):
            print(f"  [{score:.4f}] {describe(chunk_by_id[chunk_id])}")

        print("  -- hybrid + reranked --")
        for result in retriever.retrieve(query, top_k=5):
            print(f"  [{result.score:.4f}] {describe(result.chunk)}")


if __name__ == "__main__":
    main()
