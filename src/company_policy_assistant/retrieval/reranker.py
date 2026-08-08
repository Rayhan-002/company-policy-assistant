from sentence_transformers import CrossEncoder

from ..ingestion.models import Chunk

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model_cache: dict[str, CrossEncoder] = {}


def get_reranker(model_name: str = DEFAULT_RERANKER_MODEL) -> CrossEncoder:
    if model_name not in _model_cache:
        _model_cache[model_name] = CrossEncoder(model_name, device="cpu")
    return _model_cache[model_name]


def rerank(
    query: str,
    candidates: list[tuple[str, Chunk]],
    top_k: int = 5,
    model_name: str = DEFAULT_RERANKER_MODEL,
) -> list[tuple[str, float]]:
    if not candidates:
        return []
    model = get_reranker(model_name)
    pairs = [(query, chunk.text) for _chunk_id, chunk in candidates]
    scores = model.predict(pairs)
    ranked = sorted(
        zip((chunk_id for chunk_id, _chunk in candidates), scores),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [(chunk_id, float(score)) for chunk_id, score in ranked[:top_k]]
