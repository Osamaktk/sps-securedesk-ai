from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


DOCUMENTS_DIRECTORY = Path(__file__).resolve().parent / "documents"


class UnsupportedDocumentTypeError(ValueError):
    """Raised when no loader is registered for a document extension."""


@dataclass(frozen=True)
class LoadedDocument:
    document_name: str
    content: str
    source_path: str
    created_at: datetime


def _document_created_at(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_ctime, tz=timezone.utc)


def load_txt_document(path: str | Path) -> LoadedDocument:
    document_path = Path(path).resolve()
    if document_path.suffix.lower() != ".txt":
        raise UnsupportedDocumentTypeError("Only .txt documents are currently supported")
    if not document_path.is_file():
        raise FileNotFoundError(f"Knowledge-base document not found: {document_path.name}")

    return LoadedDocument(
        document_name=document_path.name,
        content=document_path.read_text(encoding="utf-8-sig"),
        source_path=str(document_path),
        created_at=_document_created_at(document_path),
    )


DocumentLoader = Callable[[str | Path], LoadedDocument]
DOCUMENT_LOADERS: dict[str, DocumentLoader] = {
    ".txt": load_txt_document,
}


def load_document(path: str | Path) -> LoadedDocument:
    document_path = Path(path)
    loader = DOCUMENT_LOADERS.get(document_path.suffix.lower())
    if loader is None:
        raise UnsupportedDocumentTypeError(
            f"No loader is registered for {document_path.suffix or 'extensionless'} files"
        )
    return loader(document_path)


def load_all_documents(
    documents_directory: Path = DOCUMENTS_DIRECTORY,
) -> list[LoadedDocument]:
    documents_directory.mkdir(parents=True, exist_ok=True)
    return [
        load_document(path)
        for path in sorted(documents_directory.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in DOCUMENT_LOADERS
    ]
