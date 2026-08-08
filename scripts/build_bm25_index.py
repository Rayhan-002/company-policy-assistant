"""Build the BM25 index over the corpus chunks and save it to data/index/."""

from company_policy_assistant.ingestion import build_chunks
from company_policy_assistant.retrieval import BM25Index


def main() -> None:
    chunks = build_chunks()
    index = BM25Index.build(chunks)
    index.save()
    print(f"Saved BM25 index ({len(index.chunk_ids)} chunks) to data/index/")


if __name__ == "__main__":
    main()
