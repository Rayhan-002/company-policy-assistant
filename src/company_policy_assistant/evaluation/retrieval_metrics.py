import math


def recall_at_k(retrieved_ids: list[str], gold_ids: set[str], k: int) -> float | None:
    if not gold_ids:
        return None
    retrieved_top_k = set(retrieved_ids[:k])
    return len(retrieved_top_k & gold_ids) / len(gold_ids)


def precision_at_k(retrieved_ids: list[str], gold_ids: set[str], k: int) -> float | None:
    if not gold_ids:
        return None
    retrieved_top_k = retrieved_ids[:k]
    if not retrieved_top_k:
        return 0.0
    hits = sum(1 for cid in retrieved_top_k if cid in gold_ids)
    return hits / len(retrieved_top_k)


def reciprocal_rank(retrieved_ids: list[str], gold_ids: set[str]) -> float | None:
    if not gold_ids:
        return None
    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in gold_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: list[str], gold_ids: set[str], k: int) -> float | None:
    if not gold_ids:
        return None
    retrieved_top_k = retrieved_ids[:k]
    dcg = sum(
        1.0 / math.log2(rank + 1) for rank, cid in enumerate(retrieved_top_k, start=1) if cid in gold_ids
    )
    ideal_hits = min(len(gold_ids), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


def mean(values: list[float | None]) -> float | None:
    present = [v for v in values if v is not None]
    return sum(present) / len(present) if present else None
