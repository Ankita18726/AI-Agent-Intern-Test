from app.config import KNOWLEDGE_BASE_DIR
from app.retrieval.chunker import chunk_documents
from app.retrieval.loader import load_knowledge_base


def test_chunks_are_created():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    chunks = chunk_documents(
        documents
    )

    assert len(chunks) > 14


def test_chunks_preserve_metadata():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    chunks = chunk_documents(
        documents
    )

    chunk = next(
        c
        for c in chunks
        if c.metadata["filename"]
        == "01-returns-policy-current.md"
    )

    assert "document_id" in chunk.metadata
    assert "status" in chunk.metadata
    assert "heading" in chunk.metadata


def test_return_window_heading_exists():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    chunks = chunk_documents(
        documents
    )

    headings = [
        c.metadata["heading"]
        for c in chunks
        if c.metadata["filename"]
        == "01-returns-policy-current.md"
    ]

    assert (
        "Standard return window"
        in headings
    )