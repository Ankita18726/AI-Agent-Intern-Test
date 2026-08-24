from app.config import (
    CHROMA_DIR,
    KNOWLEDGE_BASE_DIR,
    create_runtime_directories,
)
from app.retrieval.chunker import chunk_documents
from app.retrieval.index import build_index
from app.retrieval.loader import load_knowledge_base


def main():

    print("=" * 70)
    print("Aster & Row Knowledge Base Index Builder")
    print("=" * 70)

    create_runtime_directories()

    # --------------------------------------------------
    # 1. Load documents
    # --------------------------------------------------

    print("\n[1/4] Loading Markdown documents...")

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    print(
        f"Loaded {len(documents)} documents."
    )

    # --------------------------------------------------
    # 2. Chunk documents
    # --------------------------------------------------

    print("\n[2/4] Creating semantic chunks...")

    chunks = chunk_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    # --------------------------------------------------
    # 3. Create embeddings + Chroma
    # --------------------------------------------------

    print("\n[3/4] Creating embeddings and ChromaDB index...")

    build_index(
        chunks
    )

    # --------------------------------------------------
    # 4. Done
    # --------------------------------------------------

    print("\n[4/4] Indexing complete.")

    print(
        f"\nChromaDB location:\n{CHROMA_DIR}"
    )

    print("\nReady for retrieval.")


if __name__ == "__main__":
    main()