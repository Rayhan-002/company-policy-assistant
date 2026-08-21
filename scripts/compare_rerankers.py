"""Compare two saved retrieval-eval result files (from scripts/eval_single_reranker.py).

Usage: uv run python scripts/compare_rerankers.py baseline.json alternative.json
Reads pre-computed results rather than loading both reranker models in one process -
this machine is RAM-constrained and can't hold two transformer models at once.
"""

import json
import sys

from company_policy_assistant.evaluation import aggregate_by_category, aggregate_stage_metrics
from company_policy_assistant.evaluation.retrieval_eval import QuestionRetrievalResult


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def load_results(path: str) -> list[QuestionRetrievalResult]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [QuestionRetrievalResult(**d) for d in data]


def main() -> None:
    baseline_path, alternative_path = sys.argv[1], sys.argv[2]
    baseline_results = load_results(baseline_path)
    alternative_results = load_results(alternative_path)

    baseline_metrics = aggregate_stage_metrics(baseline_results, "reranked")
    alternative_metrics = aggregate_stage_metrics(alternative_results, "reranked")

    print("## Overall (reranked stage)")
    print("| Reranker | N | Recall@5 | Recall@10 | Precision@5 | MRR | nDCG@5 |")
    print("|---|---|---|---|---|---|---|")
    for label, m in [("Baseline", baseline_metrics), ("Alternative", alternative_metrics)]:
        print(
            f"| {label} | {m.n_questions} | {fmt(m.recall_at_5)} | {fmt(m.recall_at_10)} | "
            f"{fmt(m.precision_at_5)} | {fmt(m.mrr)} | {fmt(m.ndcg_at_5)} |"
        )

    baseline_by_cat = aggregate_by_category(baseline_results, "reranked")
    alternative_by_cat = aggregate_by_category(alternative_results, "reranked")

    print("\n## By category")
    print("| Category | N | Baseline Recall@5 | Alt Recall@5 | Baseline MRR | Alt MRR |")
    print("|---|---|---|---|---|---|")
    for category in sorted(baseline_by_cat):
        b, a = baseline_by_cat[category], alternative_by_cat[category]
        print(
            f"| {category} | {b.n_questions} | {fmt(b.recall_at_5)} | {fmt(a.recall_at_5)} | "
            f"{fmt(b.mrr)} | {fmt(a.mrr)} |"
        )

    watch_ids = {"applicability-001", "version-001", "version-002"}
    baseline_by_id = {r.question_id: r for r in baseline_results}
    alternative_by_id = {r.question_id: r for r in alternative_results}

    print("\n## Known-hard questions")
    for qid in sorted(watch_ids):
        if qid not in baseline_by_id:
            continue
        gold = set(baseline_by_id[qid].gold_chunk_ids)
        b_hit = bool(gold & set(baseline_by_id[qid].reranked_chunk_ids[:5]))
        a_hit = bool(gold & set(alternative_by_id[qid].reranked_chunk_ids[:5]))
        print(f"  {qid}: baseline_hit@5={b_hit}  alternative_hit@5={a_hit}")


if __name__ == "__main__":
    main()
