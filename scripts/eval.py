"""Run the full evaluation: retrieval metrics (hybrid vs. reranked) + generation-quality judging.

Usage: uv run python scripts/eval.py
Generation judging requires GROQ_API_KEY or GEMINI_API_KEY in .env — retrieval-only
metrics run without one; that step is skipped (with a clear message) if no key is set.

Writes eval/results/latest.json (raw data) and eval/results/latest.md (human-readable report).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from company_policy_assistant.evaluation import (  # noqa: E402
    RetryingLLMProvider,
    aggregate_by_category,
    aggregate_stage_metrics,
    collect_retrieval_results,
    load_benchmark,
    run_generation_eval,
)
from company_policy_assistant.generation import get_llm_provider  # noqa: E402
from company_policy_assistant.ingestion import build_chunks  # noqa: E402
from company_policy_assistant.retrieval import BM25Index, Retriever, VectorIndex  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parents[1] / "eval" / "results"


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def stage_metrics_row(label: str, m) -> str:
    return f"| {label} | {m.n_questions} | {fmt(m.recall_at_5)} | {fmt(m.recall_at_10)} | {fmt(m.precision_at_5)} | {fmt(m.mrr)} | {fmt(m.ndcg_at_5)} |"


def build_retrieval_report(results) -> list[str]:
    lines = ["## Retrieval: hybrid-only vs. hybrid + reranked", ""]
    lines.append("| Stage | N | Recall@5 | Recall@10 | Precision@5 | MRR | nDCG@5 |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(stage_metrics_row("Hybrid only", aggregate_stage_metrics(results, "hybrid")))
    lines.append(stage_metrics_row("Hybrid + reranked", aggregate_stage_metrics(results, "reranked")))
    lines.append("")

    lines.append("### By category")
    lines.append("")
    lines.append("| Category | N | Hybrid Recall@5 | Reranked Recall@5 | Hybrid MRR | Reranked MRR |")
    lines.append("|---|---|---|---|---|---|")
    hybrid_by_cat = aggregate_by_category(results, "hybrid")
    reranked_by_cat = aggregate_by_category(results, "reranked")
    for category in sorted(hybrid_by_cat):
        h, r = hybrid_by_cat[category], reranked_by_cat[category]
        lines.append(
            f"| {category} | {h.n_questions} | {fmt(h.recall_at_5)} | {fmt(r.recall_at_5)} | {fmt(h.mrr)} | {fmt(r.mrr)} |"
        )
    lines.append("")
    return lines


def build_generation_report(results) -> list[str]:
    lines = ["## Generation quality (LLM-judge)", ""]
    lines.append(
        "Caveat: the same LLM provider both generates and judges answers here (no separate/stronger "
        "judge model configured) — treat this as a directional signal, not an unbiased score."
    )
    lines.append("")

    errored = [r for r in results if r.error]
    judged = [r for r in results if not r.error]

    faithful_rate = sum(1 for r in judged if r.faithful) / len(judged) if judged else None
    correct_rate = sum(1 for r in judged if r.correct) / len(judged) if judged else None

    lines.append(f"Judged: {len(judged)}/{len(results)} (errors: {len(errored)})")
    lines.append(f"Faithful: {fmt(faithful_rate)} | Correct: {fmt(correct_rate)}")
    lines.append("")

    categories = sorted({r.category for r in results})
    lines.append("| Category | N | Faithful | Correct |")
    lines.append("|---|---|---|---|")
    for category in categories:
        cat_judged = [r for r in judged if r.category == category]
        if not cat_judged:
            continue
        f_rate = sum(1 for r in cat_judged if r.faithful) / len(cat_judged)
        c_rate = sum(1 for r in cat_judged if r.correct) / len(cat_judged)
        lines.append(f"| {category} | {len(cat_judged)} | {fmt(f_rate)} | {fmt(c_rate)} |")
    lines.append("")

    incorrect = [r for r in judged if not r.correct]
    if incorrect:
        lines.append("### Incorrect answers")
        lines.append("")
        for r in incorrect:
            lines.append(f"- **{r.question_id}** ({r.category}): {r.reasoning}")
        lines.append("")

    if errored:
        lines.append("### Errors")
        lines.append("")
        for r in errored:
            lines.append(f"- **{r.question_id}**: {r.error}")
        lines.append("")

    return lines


def main() -> None:
    questions = load_benchmark()
    chunks = build_chunks()
    retriever = Retriever(chunks, VectorIndex.load(), BM25Index.load())

    print(f"Running retrieval eval over {len(questions)} questions...")
    retrieval_results = collect_retrieval_results(questions, chunks, retriever)

    report_lines = [
        f"# Evaluation report — {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        *build_retrieval_report(retrieval_results),
    ]

    generation_results = []
    try:
        llm = get_llm_provider()
    except KeyError as e:
        print(f"\nSkipping generation eval: missing environment variable {e}.")
        print("Copy .env.example to .env and fill in an API key to run it.")
    else:
        print(
            f"\nRunning generation eval over {len(questions)} questions (live LLM calls, "
            "2 per question — retries with backoff on rate limits, may take a while)..."
        )
        generation_results = run_generation_eval(questions, retriever, RetryingLLMProvider(llm))
        report_lines += build_generation_report(generation_results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "latest.md").write_text("\n".join(report_lines), encoding="utf-8")
    (RESULTS_DIR / "latest.json").write_text(
        json.dumps(
            {
                "retrieval": [vars(r) for r in retrieval_results],
                "generation": [vars(r) for r in generation_results],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n" + "\n".join(report_lines))
    print(f"\nSaved report to {RESULTS_DIR / 'latest.md'} and {RESULTS_DIR / 'latest.json'}")


if __name__ == "__main__":
    main()
