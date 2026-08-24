from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from app.config import (
    CHROMA_DIR,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)
from app.retrieval.chunker import DocumentChunk


COLLECTION_NAME = "aster_row_knowledge_base"


def create_embeddings() -> OllamaEmbeddings:
    """
    Create the local Ollama embedding model.
    """

    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def create_vector_store() -> Chroma:
    """
    Connect to the persistent ChromaDB collection.
    """

    embeddings = create_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

def clear_index() -> None:
    """
    Delete the existing Chroma collection.
    """

    vector_store = create_vector_store()

    try:
        vector_store.delete_collection()
    except Exception:
        pass
def build_index(
    chunks: list[DocumentChunk],
) -> Chroma:
    """
    Create/update the ChromaDB index from document chunks.
    """

    vector_store = create_vector_store()

    documents = [
        Document(
            page_content=chunk.text,
            metadata=chunk.metadata,
        )
        for chunk in chunks
    ]

    ids = [
        chunk.chunk_id
        for chunk in chunks
    ]
    for doc in documents:
        for key, value in doc.metadata.items():
            if value is not None and not isinstance(value, (str, int, float, bool, list)):
                doc.metadata[key] = str(value)
    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    return vector_store