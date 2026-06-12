from fastapi import APIRouter, HTTPException, status

from ai.chat.session import SessionOwnershipError
from ai.llm.router import LLMGenerationError
from ai.schemas.chat import ChatRequest, ChatResponse
from ai.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return ChatService().respond(request)
    except SessionOwnershipError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
