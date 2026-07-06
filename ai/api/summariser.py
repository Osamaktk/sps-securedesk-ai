from fastapi import APIRouter

from ai.schemas.summariser import SummariserRequest, SummariserResponse
from ai.services.summariser_service import SummariserService


router = APIRouter(prefix="/summarise", tags=["summariser"])


@router.post("", response_model=SummariserResponse)
def summarise(request: SummariserRequest) -> SummariserResponse:
    return SummariserService().summarise(request)