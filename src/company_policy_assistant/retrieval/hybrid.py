from .bm25_index import BM25Index
from .embeddings import embed_query
from .vector_index import VectorIndex

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    ranked_lists: list[list[tuple[str, float]]], k: int = DEFAULT_RRF_K
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, (chunk_id, _score) in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)


class HybridRetriever:
    def __init__(self, vector_index: VectorIndex, bm25_index: BM25Index):
        self.vector_index = vector_index
        self.bm25_index = bm25_index

    def search(self, query: str, top_k: int = 10, candidate_k: int = 20) -> list[tuple[str, float]]:
        query_vector = embed_query(query)
        dense_results = self.vector_index.search(query_vector, top_k=candidate_k)
        sparse_results = self.bm25_index.search(query, top_k=candidate_k)
        fused = reciprocal_rank_fusion([dense_results, sparse_results])
        return fused[:top_k]
