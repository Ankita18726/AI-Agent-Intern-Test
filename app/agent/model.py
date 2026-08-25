from langchain_ollama import ChatOllama

from app.config import (
    LLM_MODEL,
    OLLAMA_BASE_URL,
)


def create_llm() -> ChatOllama:
    """
    Create the local Ollama chat model.
    """

    return ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
        num_predict=300,
        num_ctx=4096,
    )