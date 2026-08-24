from app.config import (
    CHROMA_DIR,
    DATA_DIR,
    EVALUATION_DIR,
    KNOWLEDGE_BASE_DIR,
    LOG_DIR,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    EMBEDDING_MODEL,
    create_runtime_directories,
)


def main():
    print("=" * 60)
    print("Aster & Row Support Agent - Setup Check")
    print("=" * 60)

    print()

    # API key
    if OPENAI_API_KEY:
        print("[OK] OpenAI API key is configured")
    else:
        print("[ERROR] OpenAI API key is missing")

    # Models
    print(f"[OK] LLM model: {OPENAI_MODEL}")
    print(f"[OK] Embedding model: {EMBEDDING_MODEL}")

    print()

    # Directories
    print(f"[CHECK] Knowledge base: {KNOWLEDGE_BASE_DIR}")
    print(f"[CHECK] Data:           {DATA_DIR}")
    print(f"[CHECK] Evaluation:     {EVALUATION_DIR}")
    print(f"[CHECK] Chroma:         {CHROMA_DIR}")
    print(f"[CHECK] Logs:           {LOG_DIR}")

    print()

    if KNOWLEDGE_BASE_DIR.exists():
        files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))
        print(
            f"[OK] Knowledge base contains "
            f"{len(files)} Markdown files"
        )
    else:
        print("[ERROR] Knowledge base directory missing")

    orders_file = DATA_DIR / "orders.json"

    if orders_file.exists():
        print("[OK] orders.json found")
    else:
        print("[ERROR] orders.json missing")

    evaluation_file = EVALUATION_DIR / "visible-cases.json"

    if evaluation_file.exists():
        print("[OK] visible-cases.json found")
    else:
        print("[ERROR] visible-cases.json missing")

    # Runtime directories
    create_runtime_directories()

    print()
    print("[OK] Runtime directories ready")

    print()
    print("=" * 60)
    print("Setup check complete")
    print("=" * 60)


if __name__ == "__main__":
    main()