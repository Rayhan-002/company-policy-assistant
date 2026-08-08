from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# bge models are trained asymmetrically: queries need this instruction prefix
# for retrieval quality, passages/chunks do not. See BAAI/bge-small-en-v1.5 model card.
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

_model_cache: dict[str, SentenceTransformer] = {}


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    if model_name not in _model_cache:
        _model_cache[model_name] = SentenceTransformer(model_name, device="cpu")
    return _model_cache[model_name]


def embed_passages(texts: list[str], model_name: str = DEFAULT_MODEL_NAME):
    model = get_embedding_model(model_name)
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def embed_query(text: str, model_name: str = DEFAULT_MODEL_NAME):
    model = get_embedding_model(model_name)
    return model.encode(
        [QUERY_INSTRUCTION + text], normalize_embeddings=True, show_progress_bar=False
    )[0]
