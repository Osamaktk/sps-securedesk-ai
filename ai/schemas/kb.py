from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class KnowledgeBaseDocumentRequest(BaseModel):
    filename: str = Field(min_length=5, max_length=255)
    content: str = Field(min_length=1)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        filename = value.strip()
        if not filename.lower().endswith(".txt"):
            raise ValueError("Only .txt knowledge-base documents are supported")
        if filename in {".", ".."} or "/" in filename or "\\" in filename:
            raise ValueError("Filename must not contain a path")
        return filename


class KnowledgeBaseDocumentUpdateRequest(BaseModel):
    content: str = Field(min_length=1)


class KnowledgeBaseDocumentResponse(BaseModel):
    filename: str
    chunk_count: int = Field(ge=0)
    created_at: datetime | None = None


class KnowledgeBaseMutationResponse(BaseModel):
    status: str
    filename: str
    chunk_count: int = Field(ge=0)


class KnowledgeBaseDeleteResponse(BaseModel):
    status: str
    filename: str
    deleted_chunks: int = Field(ge=0)


class KnowledgeBaseSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5_000)
    top_k: int | None = Field(default=None, ge=1, le=5)


class KnowledgeBaseSearchResult(BaseModel):
    content: str
    score: float = Field(ge=0.0, le=1.0)
    document_name: str
    section: str
    chunk_id: str
    source_path: str
    created_at: datetime
    citation: str


class KnowledgeBaseSearchResponse(BaseModel):
    results: list[KnowledgeBaseSearchResult] = Field(default_factory=list)
    status: str
    answer_available: bool
    message: str | None = None
