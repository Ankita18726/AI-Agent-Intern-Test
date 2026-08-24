from app.config import KNOWLEDGE_BASE_DIR
from app.retrieval.chunker import chunk_documents
from app.retrieval.loader import load_knowledge_base


def main():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    chunks = chunk_documents(
        documents
    )

    print(
        f"Documents: {len(documents)}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print()

    for chunk in chunks[:10]:

        print("=" * 70)

        print(
            f"Chunk ID: {chunk.chunk_id}"
        )

        print(
            f"File: "
            f"{chunk.metadata['filename']}"
        )

        print(
            f"Heading: "
            f"{chunk.metadata['heading']}"
        )

        print(
            f"Status: "
            f"{chunk.metadata['status']}"
        )

        print()

        print(chunk.text[:300])


if __name__ == "__main__":
    main()