from functools import lru_cache

from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


@lru_cache
def get_embedding_function() -> EmbeddingFunction:
    """Return Chroma's local semantic embedding model."""

    return DefaultEmbeddingFunction()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = get_embedding_function()(texts)
    return [list(map(float, embedding)) for embedding in embeddings]
