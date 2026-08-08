import json
from pathlib import Path

import faiss
import numpy as np

from ..ingestion.models import Chunk
from .embeddings import embed_passages

DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "index"


class VectorIndex:
    def __init__(self, index: faiss.Index, chunk_ids: list[str]):
        self.index = index
        self.chunk_ids = chunk_ids

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "VectorIndex":
        embeddings = np.asarray(embed_passages([c.text for c in chunks]), dtype="float32")
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        return cls(index, [c.chunk_id for c in chunks])

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[tuple[str, float]]:
        query_vector = np.asarray(query_vector, dtype="float32").reshape(1, -1)
        scores, indices = self.index.search(query_vector, top_k)
        return [
            (self.chunk_ids[idx], float(score))
            for idx, score in zip(indices[0], scores[0])
            if idx != -1
        ]

    def save(self, directory: Path = DEFAULT_INDEX_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(directory / "faiss.index"))
        (directory / "chunk_ids.json").write_text(json.dumps(self.chunk_ids), encoding="utf-8")

    @classmethod
    def load(cls, directory: Path = DEFAULT_INDEX_DIR) -> "VectorIndex":
        index = faiss.read_index(str(directory / "faiss.index"))
        chunk_ids = json.loads((directory / "chunk_ids.json").read_text(encoding="utf-8"))
        return cls(index, chunk_ids)
