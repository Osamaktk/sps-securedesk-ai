from ai.schemas.summariser import SummariserRequest, SummariserResponse
from ai.summariser.summarise import summarise_text


class SummariserService:
    def summarise(self, request: SummariserRequest) -> SummariserResponse:
        return summarise_text(request)
