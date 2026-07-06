from fastapi import APIRouter, HTTPException, status

from ai.schemas.classifier import ClassifierRequest, ClassifierResponse
from ai.services.classifier_service import ClassifierService


router = APIRouter(prefix="/classify", tags=["classifier"])


@router.post("", response_model=ClassifierResponse)
def classify(request: ClassifierRequest) -> ClassifierResponse:
    return ClassifierService().classify(request)