from dataclasses import dataclass
from pathlib import Path

from ..ingestion import Chunk, build_chunks
from .bm25_index import BM25Index
from .hybrid import DEFAULT_CANDIDATE_K, HybridRetriever
from .reranker import rerank
from .vector_index import VectorIndex

DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "index"


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, chunks: list[Chunk], vector_index: VectorIndex, bm25_index: BM25Index):
        self.chunk_by_id = {c.chunk_id: c for c in chunks}
        self.hybrid = HybridRetriever(vector_index, bm25_index)

    @classmethod
    def load(cls, index_dir: Path = DEFAULT_INDEX_DIR) -> "Retriever":
        chunks = build_chunks()
        vector_index = VectorIndex.load(index_dir)
        bm25_index = BM25Index.load(index_dir)
        return cls(chunks, vector_index, bm25_index)

    def retrieve(self, query: str, top_k: int = 5, candidate_k: int = DEFAULT_CANDIDATE_K) -> list[RetrievedChunk]:
        candidates = self.hybrid.search(query, top_k=candidate_k)
        candidate_chunks = [(chunk_id, self.chunk_by_id[chunk_id]) for chunk_id, _score in candidates]
        reranked = rerank(query, candidate_chunks, top_k=top_k)
        return [RetrievedChunk(self.chunk_by_id[chunk_id], score) for chunk_id, score in reranked]
