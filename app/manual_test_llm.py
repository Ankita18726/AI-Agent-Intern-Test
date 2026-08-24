from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL


def main():
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from .env"
        )

    print("Connecting to OpenAI...")

    model = ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
    )

    response = model.invoke(
        "Reply with exactly: Aster & Row setup works."
    )

    print()
    print("Model response:")
    print(response.content)


if __name__ == "__main__":
    main()