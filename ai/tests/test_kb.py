import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from ai.config.settings import get_settings
from ai.kb.chunker import chunk_text
from ai.kb.loader import load_all_documents
from ai.kb.retriever import search
from ai.kb.vector_store import VectorSearchResult
from ai.schemas.kb import KnowledgeBaseDocumentRequest


class FakeVectorStore:
    def __init__(self, results: list[VectorSearchResult] | None = None) -> None:
        self.results = results or []
        self.requested_top_k: int | None = None

    def search(self, query: str, top_k: int) -> list[VectorSearchResult]:
        del query
        self.requested_top_k = top_k
        return self.results[:top_k]


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()

    def test_loader_finds_all_sample_documents(self) -> None:
        documents = load_all_documents()

        self.assertEqual(len(documents), 10)
        self.assertTrue(all(document.document_name.endswith(".txt") for document in documents))

    def test_chunking_preserves_sections_metadata_and_overlap(self) -> None:
        text = "# Section 1: Overview\n" + ("alpha beta gamma " * 100)
        chunks = chunk_text(
            text,
            "Guide.txt",
            source_path="documents/Guide.txt",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            chunk_size=200,
            overlap=50,
        )

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.section == "Section 1: Overview" for chunk in chunks))
        self.assertTrue(all(chunk.document_name == "Guide.txt" for chunk in chunks))
        self.assertEqual(len({chunk.chunk_id for chunk in chunks}), len(chunks))
        self.assertIn(chunks[0].content[-40:].strip(), chunks[1].content)

    def test_document_request_rejects_paths_and_non_txt_files(self) -> None:
        invalid_names = ("guide.pdf", "../guide.txt", "folder\\guide.txt")
        for filename in invalid_names:
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError):
                    KnowledgeBaseDocumentRequest(filename=filename, content="content")

    def test_retrieval_filters_low_scores_and_adds_citations(self) -> None:
        created_at = "2026-01-01T00:00:00+00:00"
        store = FakeVectorStore(
            [
                VectorSearchResult(
                    content="Reset the compromised password.",
                    distance=0.2,
                    metadata={
                        "document_name": "Phishing Response Guide.txt",
                        "section": "Section 2: Steps",
                        "chunk_id": "chunk-1",
                        "source_path": "documents/Phishing Response Guide.txt",
                        "created_at": created_at,
                    },
                ),
                VectorSearchResult(
                    content="Unrelated content.",
                    distance=0.9,
                    metadata={
                        "document_name": "Other.txt",
                        "section": "General",
                        "chunk_id": "chunk-2",
                        "source_path": "documents/Other.txt",
                        "created_at": created_at,
                    },
                ),
            ]
        )

        with patch.dict(
            "os.environ",
            {"KB_MIN_SIMILARITY_SCORE": "0.35"},
            clear=False,
        ):
            get_settings.cache_clear()
            results = search("compromised password", 5, vector_store=store)

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].citation,
            "Source: Phishing Response Guide.txt, Section 2: Steps",
        )

    def test_empty_store_returns_no_results(self) -> None:
        self.assertEqual(search("anything", vector_store=FakeVectorStore()), [])


if __name__ == "__main__":
    unittest.main()
