from langchain_ollama import OllamaEmbeddings

from app.config import (
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
)


def main():

    print("=" * 60)
    print("Testing Ollama Embeddings")
    print("=" * 60)

    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    text = "Aster and Row return policy"

    vector = embeddings.embed_query(text)

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Vector length: {len(vector)}")
    print(f"First five values: {vector[:5]}")

    print()
    print("Embedding model works.")


if __name__ == "__main__":
    main()