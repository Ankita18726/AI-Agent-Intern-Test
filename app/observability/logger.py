import json
from datetime import datetime
from threading import Lock
from typing import Any

from app.config import (
    ENABLE_TRACING,
    TRACE_PATH,
    create_runtime_directories,
)
from app.observability.sanitizer import (
    sanitize_value,
)


_WRITE_LOCK = Lock()

def summarize_retrieval(
    passages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert retrieved passages into a concise trace format.
    """

    output = []

    for passage in passages:

        metadata = passage.get(
            "metadata",
            {},
        )

        text = passage.get(
            "text",
            "",
        )

        output.append(
            {
                "filename":
                    metadata.get(
                        "filename"
                    ),

                "heading":
                    metadata.get(
                        "heading"
                    ),

                "document_id":
                    metadata.get(
                        "document_id"
                    ),

                "status":
                    metadata.get(
                        "status"
                    ),

                "audience":
                    metadata.get(
                        "audience"
                    ),

                "policy_authority":
                    metadata.get(
                        "policy_authority"
                    ),

                "semantic_score":
                    passage.get(
                        "semantic_score"
                    ),

                "lexical_score":
                    passage.get(
                        "lexical_score"
                    ),

                "precedence_score":
                    passage.get(
                        "precedence_score"
                    ),

                "final_score":
                    passage.get(
                        "final_score"
                    ),

                # Keep a limited text preview rather than logging
                # every retrieved chunk in full.
                "text_preview":
                    text[:500],
            }
        )

    return output
def build_tool_trace(
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Construct tool-call information from final graph state.
    """

    if not state.get(
        "tool_called",
        False,
    ):
        return []

    order_id = state.get(
        "requested_order_id"
    )

    result = state.get(
        "order_result"
    )

    return [
        {
            "tool":
                "order_lookup",

            "arguments": {
                "order_id":
                    order_id,
            },

            "result":
                sanitize_value(
                    result
                ),
        }
    ]
def build_turn_trace(
    session_id: str,
    user_message: str,
    state: dict[str, Any],
    duration_ms: float | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """
    Construct one complete trace for a user turn.
    """

    history = state.get(
        "history",
        [],
    )

    # The final history includes the current user and assistant
    # message, so keep only a limited recent context.
    recent_history = history[-8:]

    retrieved = state.get(
        "retrieved_passages",
        [],
    )

    return {
        "timestamp":
            utc_timestamp(),

        "session_id":
            session_id,

        "user_message":
            user_message,

        "route":
            state.get(
                "route"
            ),

        "route_reason":
            state.get(
                "route_reason"
            ),

        "conversation_history":
            recent_history,

        "retrieval_query":
            state.get(
                "retrieval_query"
            ),

        "retrieved_passages":
            summarize_retrieval(
                retrieved
            ),

        "tool_calls":
            build_tool_trace(
                state
            ),

        "safety": {
            "blocked":
                state.get(
                    "blocked",
                    False,
                ),

            "conflict_detected":
                state.get(
                    "conflict_detected",
                    False,
                ),

            "insufficient_information":
                state.get(
                    "insufficient_information",
                    False,
                ),

            "review_required":
                state.get(
                    "review_required",
                    False,
                ),
        },

        "handoff": {
            "recommended":
                state.get(
                    "handoff",
                    False,
                ),

            "reason":
                state.get(
                    "handoff_reason"
                ),
        },

        "sources":
            state.get(
                "sources",
                [],
            ),

        "final_response":
            state.get(
                "answer",
                "",
            ),

        "duration_ms":
            duration_ms,

        "error":
            error,
    }
def utc_timestamp() -> str:
    """
    Return an ISO-formatted timestamp.
    """

    return (
        datetime.now()
        .astimezone()
        .isoformat()
    )


def write_trace(
    trace: dict[str, Any],
) -> None:
    """
    Append one sanitized trace to the JSONL file.

    Logging failures should never crash the support agent.
    """

    if not ENABLE_TRACING:
        return

    try:

        create_runtime_directories()

        sanitized = sanitize_value(
            trace
        )

        line = json.dumps(
            sanitized,
            ensure_ascii=False,
            default=str,
        )

        with _WRITE_LOCK:

            with TRACE_PATH.open(
                "a",
                encoding="utf-8",
            ) as file:

                file.write(
                    line
                    + "\n"
                )

    except Exception as exc:

        # Observability must not break customer support.
        print(
            "[TRACE ERROR]",
            type(exc).__name__,
            str(exc),
        )