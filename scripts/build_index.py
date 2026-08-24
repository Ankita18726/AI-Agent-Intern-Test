import sys
from collections import Counter

from app.config import (
    CHROMA_DIR,
    KNOWLEDGE_BASE_DIR,
    create_runtime_directories,
)

from app.retrieval.chunker import chunk_documents

from app.retrieval.index import (
    build_index,
    clear_index,
)

from app.retrieval.loader import load_knowledge_base


def main():

    clean = "--clean" in sys.argv

    print("=" * 70)
    print("Aster & Row Knowledge Base Index Builder")
    print("=" * 70)

    # ---------------------------------------------------------
    # Create required runtime directories
    # ---------------------------------------------------------

    create_runtime_directories()

    # ---------------------------------------------------------
    # Optional clean rebuild
    # ---------------------------------------------------------

    if clean:

        print("\n[0/4] Clearing existing index...")

        clear_index()

    # ---------------------------------------------------------
    # Step 1: Load documents
    # ---------------------------------------------------------

    print("\n[1/4] Loading Markdown documents...")

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    print(
        f"Loaded {len(documents)} documents."
    )

    # ---------------------------------------------------------
    # Step 2: Chunk documents
    # ---------------------------------------------------------

    print("\n[2/4] Creating semantic chunks...")

    chunks = chunk_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    # ---------------------------------------------------------
    # Step 3: Build ChromaDB index
    # ---------------------------------------------------------

    print(
        "\n[3/4] Creating embeddings and ChromaDB index..."
    )

    build_index(
        chunks
    )

    # ---------------------------------------------------------
    # Step 4: Complete
    # ---------------------------------------------------------

    print("\n[4/4] Indexing complete.")

    print(
        f"\nChromaDB location:\n{CHROMA_DIR}"
    )

    # ---------------------------------------------------------
    # Index statistics
    # ---------------------------------------------------------

    status_counts = Counter(
        chunk.metadata.get("status", "unknown")
        for chunk in chunks
    )

    audience_counts = Counter(
        chunk.metadata.get("audience", "unknown")
        for chunk in chunks
    )

    print("\n" + "=" * 70)
    print("Index Summary")
    print("=" * 70)

    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Status distribution: "
        f"{dict(status_counts)}"
    )

    print(
        f"Audience distribution: "
        f"{dict(audience_counts)}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()