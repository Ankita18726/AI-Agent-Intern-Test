import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge-base"
DATA_DIR = PROJECT_ROOT / "data"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"

CHROMA_DIR = PROJECT_ROOT / os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "chroma_db",
)

LOG_DIR = PROJECT_ROOT / os.getenv(
    "LOG_DIRECTORY",
    "logs",
)


# --------------------------------------------------
# Ollama configuration
# --------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama3.1:8b",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text",
)


# --------------------------------------------------
# Validation
# --------------------------------------------------

def validate_config() -> None:

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {KNOWLEDGE_BASE_DIR}"
        )

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Data directory not found: {DATA_DIR}"
        )

    if not EVALUATION_DIR.exists():
        raise FileNotFoundError(
            f"Evaluation directory not found: {EVALUATION_DIR}"
        )


def create_runtime_directories() -> None:

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )