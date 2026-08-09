from dataclasses import dataclass

from ..ingestion import Chunk, build_chunks
from ..retrieval import BM25Index, HybridRetriever, Retriever, VectorIndex
from .models import BenchmarkQuestion
from .resolve import load_benchmark, resolve_gold_chunk_ids
from .retrieval_metrics import mean, ndcg_at_k, precision_at_k, reciprocal_rank, recall_at_k

EVAL_TOP_K = 10


@dataclass
class QuestionRetrievalResult:
    question_id: str
    category: str
    gold_chunk_ids: list[str]
    hybrid_chunk_ids: list[str]
    reranked_chunk_ids: list[str]


@dataclass
class StageMetrics:
    n_questions: int
    recall_at_5: float | None
    recall_at_10: float | None
    precision_at_5: float | None
    mrr: float | None
    ndcg_at_5: float | None


def collect_retrieval_results(
    questions: list[BenchmarkQuestion], chunks: list[Chunk], retriever: Retriever
) -> list[QuestionRetrievalResult]:
    results = []
    for q in questions:
        gold_chunk_ids = resolve_gold_chunk_ids(q, chunks)

        hybrid_ranked = retriever.hybrid.search(q.question, top_k=EVAL_TOP_K)
        hybrid_chunk_ids = [chunk_id for chunk_id, _score in hybrid_ranked]

        reranked = retriever.retrieve(q.question, top_k=EVAL_TOP_K)
        reranked_chunk_ids = [r.chunk.chunk_id for r in reranked]

        results.append(
            QuestionRetrievalResult(
                question_id=q.id,
                category=q.category,
                gold_chunk_ids=gold_chunk_ids,
                hybrid_chunk_ids=hybrid_chunk_ids,
                reranked_chunk_ids=reranked_chunk_ids,
            )
        )
    return results


def _stage_chunk_ids(result: QuestionRetrievalResult, stage: str) -> list[str]:
    return result.hybrid_chunk_ids if stage == "hybrid" else result.reranked_chunk_ids


def aggregate_stage_metrics(results: list[QuestionRetrievalResult], stage: str) -> StageMetrics:
    scored = [r for r in results if r.gold_chunk_ids]
    recalls5, recalls10, precisions5, rrs, ndcgs5 = [], [], [], [], []
    for r in scored:
        gold = set(r.gold_chunk_ids)
        retrieved = _stage_chunk_ids(r, stage)
        recalls5.append(recall_at_k(retrieved, gold, 5))
        recalls10.append(recall_at_k(retrieved, gold, 10))
        precisions5.append(precision_at_k(retrieved, gold, 5))
        rrs.append(reciprocal_rank(retrieved, gold))
        ndcgs5.append(ndcg_at_k(retrieved, gold, 5))
    return StageMetrics(
        n_questions=len(scored),
        recall_at_5=mean(recalls5),
        recall_at_10=mean(recalls10),
        precision_at_5=mean(precisions5),
        mrr=mean(rrs),
        ndcg_at_5=mean(ndcgs5),
    )


def aggregate_by_category(
    results: list[QuestionRetrievalResult], stage: str
) -> dict[str, StageMetrics]:
    categories = sorted({r.category for r in results})
    return {
        category: aggregate_stage_metrics([r for r in results if r.category == category], stage)
        for category in categories
    }


def run_retrieval_eval() -> list[QuestionRetrievalResult]:
    questions = load_benchmark()
    chunks = build_chunks()
    retriever = Retriever(chunks, VectorIndex.load(), BM25Index.load())
    return collect_retrieval_results(questions, chunks, retriever)
