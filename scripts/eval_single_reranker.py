"""Run retrieval-only eval with a single reranker model and save results to JSON.

Usage: uv run python scripts/eval_single_reranker.py <model-id> <output-path>
Kept as a separate process (not compared in-process with another model) so peak
memory stays low - this machine is RAM-constrained, and holding two transformer
models resident at once reliably fails allocation here.
"""

import json
import sys
from dataclasses import asdict

from company_policy_assistant.evaluation import collect_retrieval_results, load_benchmark
from company_policy_assistant.ingestion import build_chunks
from company_policy_assistant.retrieval import BM25Index, Retriever, VectorIndex


def main() -> None:
    model_name = sys.argv[1]
    output_path = sys.argv[2]

    questions = load_benchmark()
    chunks = build_chunks()
    retriever = Retriever(chunks, VectorIndex.load(), BM25Index.load(), reranker_model=model_name)

    print(f"Running retrieval eval with reranker: {model_name}")
    results = collect_retrieval_results(questions, chunks, retriever)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print(f"Saved {len(results)} results to {output_path}")


if __name__ == "__main__":
    main()
