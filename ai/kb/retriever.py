from dataclasses import dataclass

from ai.config.settings import get_settings
from ai.kb.vector_store import VectorStore, get_vector_store


@dataclass(frozen=True)
class RetrievalResult:
    content: str
    score: float
    document_name: str
    section: str
    chunk_id: str
    source_path: str
    created_at: str

    @property
    def citation(self) -> str:
        return f"Source: {self.document_name}, {self.section}"


def search(
    query: str,
    top_k: int | None = None,
    *,
    vector_store: VectorStore | None = None,
) -> list[RetrievalResult]:
    settings = get_settings()
    limit = top_k or settings.max_kb_results
    raw_results = (vector_store or get_vector_store()).search(query, limit)

    relevant: list[RetrievalResult] = []
    for result in raw_results:
        score = max(0.0, min(1.0, 1.0 - result.distance))
        if score < settings.kb_min_similarity_score:
            continue
        metadata = result.metadata
        relevant.append(
            RetrievalResult(
                content=result.content,
                score=score,
                document_name=str(metadata["document_name"]),
                section=str(metadata["section"]),
                chunk_id=str(metadata["chunk_id"]),
                source_path=str(metadata["source_path"]),
                created_at=str(metadata["created_at"]),
            )
        )
    return relevant
