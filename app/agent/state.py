from typing import Any, Literal, TypedDict


RouteType = Literal[
    "knowledge",
    "order",
    "unsupported_action",
    "blocked",
]


class AgentState(TypedDict, total=False):
    """
    State shared by all LangGraph nodes.

    total=False means nodes can update only the
    fields they are responsible for.
    """

    # --------------------------------------------------
    # Current request
    # --------------------------------------------------

    user_message: str

    # --------------------------------------------------
    # Routing
    # --------------------------------------------------

    route: RouteType
    route_reason: str

    # --------------------------------------------------
    # Conversation context
    # --------------------------------------------------

    last_order_id: str | None
    current_topic: str | None

    # Recent conversational history.
    # We keep this intentionally small.
    history: list[dict[str, str]]

    # --------------------------------------------------
    # RAG
    # --------------------------------------------------

    retrieval_query: str

    retrieved_passages: list[dict[str, Any]]

    sources: list[dict[str, str]]

    # --------------------------------------------------
    # Order lookup
    # --------------------------------------------------

    requested_order_id: str | None

    order_result: dict[str, Any] | None

    tool_called: bool

    # --------------------------------------------------
    # Safety / grounding
    # --------------------------------------------------

    blocked: bool

    conflict_detected: bool

    insufficient_information: bool
    review_required: bool
    handoff: bool

    handoff_reason: str | None

    # --------------------------------------------------
    # Final output
    # --------------------------------------------------

    answer: str