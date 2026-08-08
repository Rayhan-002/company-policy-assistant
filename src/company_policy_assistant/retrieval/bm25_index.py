import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from ..ingestion.models import Chunk

DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "index"
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, bm25: BM25Okapi, chunk_ids: list[str]):
        self.bm25 = bm25
        self.chunk_ids = chunk_ids

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "BM25Index":
        bm25 = BM25Okapi([tokenize(c.text) for c in chunks])
        return cls(bm25, [c.chunk_id for c in chunks])

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self.chunk_ids, scores), key=lambda pair: pair[1], reverse=True)
        return [(chunk_id, float(score)) for chunk_id, score in ranked[:top_k] if score > 0]

    def save(self, directory: Path = DEFAULT_INDEX_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "bm25.pkl").open("wb") as f:
            pickle.dump({"bm25": self.bm25, "chunk_ids": self.chunk_ids}, f)

    @classmethod
    def load(cls, directory: Path = DEFAULT_INDEX_DIR) -> "BM25Index":
        with (directory / "bm25.pkl").open("rb") as f:
            data = pickle.load(f)
        return cls(data["bm25"], data["chunk_ids"])
