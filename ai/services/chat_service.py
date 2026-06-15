from ai.chat.assistant import ChatAssistant
from ai.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self, assistant: ChatAssistant | None = None) -> None:
        self._assistant = assistant or ChatAssistant()

    def respond(self, request: ChatRequest) -> ChatResponse:
        return self._assistant.respond(request)
