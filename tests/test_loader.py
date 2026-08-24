from app.config import KNOWLEDGE_BASE_DIR
from app.retrieval.loader import load_knowledge_base


def test_all_documents_load():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    assert len(documents) == 14


def test_current_returns_metadata():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    document = next(
        d
        for d in documents
        if d.filename
        == "01-returns-policy-current.md"
    )

    assert document.metadata["status"] == "active"

    assert (
        document.metadata["policy_authority"]
        == "official"
    )

    assert (
        document.metadata["document_id"]
        == "RET-2026-01"
    )


def test_legacy_returns_metadata():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    document = next(
        d
        for d in documents
        if d.filename
        == "02-returns-policy-legacy.md"
    )

    assert (
        document.metadata["status"]
        == "superseded"
    )

    assert (
        document.metadata["superseded_by"]
        == "RET-2026-01"
    )


def test_internal_migration_metadata():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    document = next(
        d
        for d in documents
        if d.filename
        == "14-internal-content-migration-notes.md"
    )

    assert (
        document.metadata["audience"]
        == "internal"
    )

    assert (
        document.metadata["policy_authority"]
        == "none"
    )

    assert (
        document.metadata["customer_answering"]
        is False
    )