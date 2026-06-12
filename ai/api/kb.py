from fastapi import APIRouter, HTTPException, status

from ai.schemas.kb import (
    KnowledgeBaseDeleteResponse,
    KnowledgeBaseDocumentRequest,
    KnowledgeBaseDocumentResponse,
    KnowledgeBaseDocumentUpdateRequest,
    KnowledgeBaseMutationResponse,
    KnowledgeBaseSearchRequest,
    KnowledgeBaseSearchResponse,
)
from ai.services.kb_service import KnowledgeBaseService


router = APIRouter(prefix="/kb", tags=["knowledge-base"])


def _service() -> KnowledgeBaseService:
    return KnowledgeBaseService()


@router.post(
    "/documents",
    response_model=KnowledgeBaseMutationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    request: KnowledgeBaseDocumentRequest,
) -> KnowledgeBaseMutationResponse:
    try:
        return _service().create(request)
    except FileExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/documents", response_model=list[KnowledgeBaseDocumentResponse])
def list_documents() -> list[KnowledgeBaseDocumentResponse]:
    return _service().list_documents()


@router.delete(
    "/documents/{filename}",
    response_model=KnowledgeBaseDeleteResponse,
)
def remove_document(filename: str) -> KnowledgeBaseDeleteResponse:
    try:
        return _service().delete(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.put(
    "/documents/{filename}",
    response_model=KnowledgeBaseMutationResponse,
)
def replace_document(
    filename: str,
    request: KnowledgeBaseDocumentUpdateRequest,
) -> KnowledgeBaseMutationResponse:
    try:
        return _service().update(filename, request.content)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/search", response_model=KnowledgeBaseSearchResponse)
def search(request: KnowledgeBaseSearchRequest) -> KnowledgeBaseSearchResponse:
    return _service().search(request)
