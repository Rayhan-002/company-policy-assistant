"""Build the FAISS vector index over the corpus chunks and save it to data/index/."""

from company_policy_assistant.ingestion import build_chunks
from company_policy_assistant.retrieval import VectorIndex


def main() -> None:
    chunks = build_chunks()
    print(f"Embedding {len(chunks)} chunks with BAAI/bge-small-en-v1.5 (CPU)...")
    index = VectorIndex.build(chunks)
    index.save()
    print(f"Saved FAISS index ({index.index.ntotal} vectors) to data/index/")


if __name__ == "__main__":
    main()
