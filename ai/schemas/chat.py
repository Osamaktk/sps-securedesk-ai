from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from ai.config.constants import TicketPrefillCategory


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1, max_length=20_000)
    created_at: datetime | None = None


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=20_000)


class TicketPrefill(BaseModel):
    source: Literal["chat"] = "chat"
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2_000)
    category: TicketPrefillCategory


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = Field(default_factory=list)
    escalate: bool = False
    ticket_prefill: TicketPrefill | None = None
