from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent.service import SupportAgent


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="Aster & Row Support Agent",
    description=(
        "Reliable RAG support agent powered by "
        "LangGraph, ChromaDB and Ollama."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# Serve frontend assets
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(
        directory=str(WEB_DIR),
    ),
    name="static",
)


# --------------------------------------------------
# API models
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    session_id: str = Field(
        min_length=1,
        max_length=200,
    )


class SourceItem(BaseModel):
    filename: str
    heading: str


class ChatResponse(BaseModel):
    answer: str

    sources: list[SourceItem] = []

    handoff: bool = False

    handoff_reason: str | None = None

    route: str | None = None


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(
        WEB_DIR / "index.html"
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "aster-row-support-agent",
    }


# --------------------------------------------------
# Chat API
# --------------------------------------------------

@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:

    try:

        # LangGraph memory uses session_id/thread_id.
        agent = SupportAgent(
            session_id=request.session_id
        )

        result: dict[str, Any] = agent.ask(
            request.message.strip()
        )

        raw_sources = result.get(
            "sources",
            [],
        )

        sources = []

        for source in raw_sources:

            filename = source.get(
                "filename"
            )

            if not filename:
                continue

            sources.append(
                SourceItem(
                    filename=filename,
                    heading=source.get(
                        "heading",
                        "Document",
                    ),
                )
            )

        return ChatResponse(
            answer=result.get(
                "answer",
                (
                    "I couldn't generate a "
                    "response."
                ),
            ),

            sources=sources,

            handoff=bool(
                result.get(
                    "handoff",
                    False,
                )
            ),

            handoff_reason=result.get(
                "handoff_reason"
            ),

            route=result.get(
                "route"
            ),
        )

    except Exception as exc:

        # Do NOT expose detailed internal traceback
        # to the customer-facing UI.

        raise HTTPException(
            status_code=500,
            detail=(
                "The support agent encountered "
                "an error. Please try again."
            ),
        ) from exc