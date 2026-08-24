from langchain_ollama import ChatOllama

from app.config import LLM_MODEL, OLLAMA_BASE_URL


def main():

    print("=" * 60)
    print("Testing Ollama")
    print("=" * 60)

    print(f"Model: {LLM_MODEL}")
    print(f"URL:   {OLLAMA_BASE_URL}")

    model = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    response = model.invoke(
        "Reply with exactly: Aster and Row Ollama setup works."
    )

    print()
    print("Model response:")
    print(response.content)

    print()
    print("Ollama connection successful.")


if __name__ == "__main__":
    main()