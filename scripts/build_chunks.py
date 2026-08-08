"""Run the ingestion pipeline over corpus/ and write chunks to data/chunks.jsonl."""

import json
from collections import Counter
from pathlib import Path

from company_policy_assistant.ingestion import build_chunks

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "chunks.jsonl"


def main() -> None:
    chunks = build_chunks()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk.model_dump_json() + "\n")

    by_document = Counter(f"{c.document_id} v{c.version}" for c in chunks)
    print(f"Wrote {len(chunks)} chunks from {len(by_document)} documents to {OUTPUT_PATH}")
    for doc, count in sorted(by_document.items()):
        print(f"  {doc}: {count} chunks")

    token_counts = [c.token_count for c in chunks]
    print(
        f"Token count per chunk — min: {min(token_counts)}, "
        f"max: {max(token_counts)}, avg: {sum(token_counts) / len(token_counts):.0f}"
    )


if __name__ == "__main__":
    main()
