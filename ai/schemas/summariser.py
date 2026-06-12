from pydantic import BaseModel, Field


class SummariserRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    max_sentences: int = Field(default=5, ge=1, le=20)


class SummariserResponse(BaseModel):
    summary: str
    key_points: list[str] = Field(default_factory=list)
    provider: str | None = None
