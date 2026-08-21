from dataclasses import dataclass
from pathlib import Path

from ..ingestion import Chunk, build_chunks
from .bm25_index import BM25Index
from .hybrid import DEFAULT_CANDIDATE_K, HybridRetriever
from .reranker import DEFAULT_RERANKER_MODEL, rerank
from .vector_index import VectorIndex
from .version_preference import prefer_active_version

DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "index"


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(
        self,
        chunks: list[Chunk],
        vector_index: VectorIndex,
        bm25_index: BM25Index,
        reranker_model: str = DEFAULT_RERANKER_MODEL,
    ):
        self.chunk_by_id = {c.chunk_id: c for c in chunks}
        self.hybrid = HybridRetriever(vector_index, bm25_index)
        self.reranker_model = reranker_model

    @classmethod
    def load(cls, index_dir: Path = DEFAULT_INDEX_DIR, reranker_model: str = DEFAULT_RERANKER_MODEL) -> "Retriever":
        chunks = build_chunks()
        vector_index = VectorIndex.load(index_dir)
        bm25_index = BM25Index.load(index_dir)
        return cls(chunks, vector_index, bm25_index, reranker_model=reranker_model)

    def retrieve(
        self, query: str, top_k: int = 5, candidate_k: int = DEFAULT_CANDIDATE_K, prefer_active: bool = True
    ) -> list[RetrievedChunk]:
        candidates = self.hybrid.search(query, top_k=candidate_k)
        candidate_chunks = [(chunk_id, self.chunk_by_id[chunk_id]) for chunk_id, _score in candidates]
        reranked = rerank(query, candidate_chunks, top_k=len(candidate_chunks), model_name=self.reranker_model)
        if prefer_active:
            reranked = prefer_active_version(reranked, self.chunk_by_id)
        reranked = reranked[:top_k]
        return [RetrievedChunk(self.chunk_by_id[chunk_id], score) for chunk_id, score in reranked]
