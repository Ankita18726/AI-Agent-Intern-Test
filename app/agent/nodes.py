import json
from app.agent.evidence_filter import (
    filter_generation_evidence,
)
from app.agent.conflicts import detect_conflict
from app.agent.evidence import (
    extract_sources,
    format_retrieved_evidence,
)
from app.agent.model import create_llm
from app.agent.prompts import (
    KNOWLEDGE_PROMPT,
    ORDER_PROMPT,
    SYSTEM_RULES,
    UNSUPPORTED_ACTION_PROMPT,
)
from app.agent.router import determine_route
from app.agent.safety import get_block_reason
from app.agent.state import AgentState
from app.retrieval.retriever import retrieve
from app.tools.order_lookup import (
    extract_order_id,
    lookup_order,
)
MIN_RELEVANCE = 0.35
MIN_SEMANTIC_RELEVANCE = 0.30
MIN_LEXICAL_RELEVANCE = 0.15
def initialize_turn(
    state: AgentState,
    
) -> dict:
    """
    Reset fields that belong only to the current turn
    while preserving conversational context.
    """
    

    return {
        "route": "knowledge",
        "route_reason": "",
        "retrieval_query": "",
        "retrieved_passages": [],
        "sources": [],
        "requested_order_id": None,
        "order_result": None,
        "tool_called": False,
        "blocked": False,
        "conflict_detected": False,
        "insufficient_information": False,
        "handoff": False,
        "handoff_reason": None,
        "answer": "",
        "review_required": False,
    }
def safety_check_node(
    state: AgentState,
) -> dict:

    message = state.get(
        "user_message",
        "",
    )

    reason = get_block_reason(
        message
    )

    if reason is None:

        return {
            "blocked": False,
        }

    if reason == "hidden_instructions":

        return {
            "blocked": True,
            "route": "blocked",
            "answer": (
                "I can't provide system prompts, "
                "hidden instructions, or internal configuration."
        ),
            "handoff": False,
        }
    elif reason == "internal_data":

        answer = (
            "I can't provide customer email, addresses, "
            "internal notes, risk scores, warehouse notes, "
            "or other internal-only data. "
            "I can help with customer-safe order information."
        )

        return {
            "blocked": True,
            "route": "blocked",
            "answer": answer,
            "handoff": True,
            "handoff_reason": (
                "Request requires access to "
                "internal-only customer data."
        ),
        }


    else:

        answer = (
            "I can't provide that information."
        )

    return {
        "blocked": True,
        "route": "blocked",
        "answer": answer,
        "handoff": True,
        "handoff_reason": (
            "Request requires access to "
            "internal-only customer data."
        ),
    }
def route_node(
    state: AgentState,
) -> dict:

    route, reason = determine_route(
        state
    )

    return {
        "route": route,
        "route_reason": reason,
    }
def build_retrieval_query(
    state: AgentState,
) -> str:
    """
    Use conversation history only for genuinely referential
    follow-up questions.

    Do NOT assume every short question is a follow-up.
    """

    message = state.get(
        "user_message",
        "",
    ).strip()

    history = state.get(
        "history",
        [],
    )

    current_topic = state.get(
        "current_topic"
    )

    lowered = message.lower()

    followup_prefixes = (
        "what about",
        "how about",
        "and what about",
        "what if",
        "and canada",
        "what about canada",
    )

    referential_phrases = (
        "when will it arrive",
        "where is it",
        "has it shipped",
        "what about that",
        "does that apply",
        "what about this",
        "what about them",
        "is that included",
        "does that include",
    )

    is_followup = (
        lowered.startswith(
            followup_prefixes
        )
        or lowered in referential_phrases
    )

    if not is_followup:
        return message

    previous_user_messages = [
        item.get(
            "content",
            ""
        )
        for item in history[-6:]
        if item.get("role") == "user"
    ]

    previous_context = " ".join(
        previous_user_messages[-2:]
    ).strip()

    if not previous_context and not current_topic:
        return message

    parts = []

    if previous_context:
        parts.append(
            f"Previous context: "
            f"{previous_context}"
        )

    if current_topic:
        parts.append(
            f"Topic: {current_topic}"
        )

    parts.append(
        f"Follow-up: {message}"
    )

    return (
    "\n".join(parts)
    + "\nAnswer the follow-up using all relevant "
      "details from the same topic, including delivery "
      "timing, fees, duties, taxes, or restrictions when asked."
)
def detect_human_review_requirement(
    query: str,
    passages: list[dict],
) -> bool:
    """
    Detect cases where retrieved policy explicitly requires
    human review before a resolution can be approved.
    """

    query_lower = query.lower()

    issue_terms = (
        "damaged",
        "defective",
        "broken",
        "wrong item",
        "incorrect item",
        "warranty",
        "replacement",
        "refund",
    )

    if not any(
        term in query_lower
        for term in issue_terms
    ):
        return False

    combined = " ".join(
        passage.get(
            "text",
            ""
        ).lower()
        for passage in passages
    )

    review_markers = (
        "human review",
        "after review",
        "before a human review is completed",
    )

    return any(
        marker in combined
        for marker in review_markers
    )
def retrieve_knowledge_node(
    state: AgentState,
) -> dict:

    query = (
        build_retrieval_query(
            state
        )
    )

    passages = retrieve(
        query,
        k=12,
    )

    relevant = []

    for passage in passages:

        semantic = (
            passage.get(
                "semantic_score",
                0,
            )
        )

        lexical = (
            passage.get(
                "lexical_score",
                0,
            )
        )

        if (
            semantic
            >= MIN_SEMANTIC_RELEVANCE
            or lexical
            >= MIN_LEXICAL_RELEVANCE
        ):

            relevant.append(
                passage
            )

    conflict = (
        detect_conflict(
            relevant
        )
    )
    review_required = (
        detect_human_review_requirement(
            query,
            relevant,
    )
)
    generation_evidence = (
        filter_generation_evidence(
            relevant
        )
    )

    # Better abstention heuristic:
    # if there is little lexical connection to the question,
    # treat the evidence as insufficient even if embeddings
    # returned generic care content.

    top_lexical = max(
        [
            passage.get(
                "lexical_score",
                0,
            )
            for passage
            in generation_evidence
        ],
        default=0,
    )

    insufficient = (
        len(
            generation_evidence
        )
        == 0
    )

    # Strong signal for unsupported material/composition claims.
    lowered = (
        state.get(
            "user_message",
            "",
        )
        .lower()
    )

    certification_terms = {
        "vegan",
        "certified",
        "certification",
        "allergic",
        "allergen",
        "adhesive",
        "materials",
    }

    asks_unverified_attribute = any(
        term in lowered
        for term
        in certification_terms
    )

    if (
        asks_unverified_attribute
        and top_lexical < 0.40
    ):
        insufficient = True

    return {
        "retrieval_query":
            query,

        "retrieved_passages":
            relevant,
        "review_required": review_required,

        "sources":
            extract_sources(
                generation_evidence
            ),

        "conflict_detected":
            conflict,

        "insufficient_information":
            insufficient,
    }
def order_lookup_node(
    state: AgentState,
) -> dict:

    message = state.get(
        "user_message",
        "",
    )

    order_id = extract_order_id(
        message
    )

    # Multi-turn fallback:
    # "Where is ORD-1007?"
    # "When will it arrive?"
    if order_id is None:

        order_id = state.get(
            "last_order_id"
        )

    # Missing ID → do not call lookup.
    if order_id is None:

        return {
            "requested_order_id": None,
            "tool_called": False,
            "order_result": None,
            "answer": (
                "Please provide your order ID, "
                "for example ORD-1007."
            ),
        }

    result = lookup_order(
        order_id
    )

    updates = {
        "requested_order_id": order_id,
        "tool_called": True,
        "order_result": result,
    }

    if result.get("found"):

        updates["last_order_id"] = (
            result.get("order_id")
        )

    else:

        updates["handoff"] = (
            result.get("reason")
            == "order_not_found"
        )

        if updates["handoff"]:

            updates["handoff_reason"] = (
                "Order ID was not found."
            )

    return updates
def knowledge_answer_node(
    state: AgentState,
) -> dict:

    retrieved_passages = (
        state.get(
            "retrieved_passages",
            [],
        )
    )

    generation_passages = (
        filter_generation_evidence(
            retrieved_passages,
            max_passages=6,
        )
    )

    insufficient = (
        state.get(
            "insufficient_information",
            False,
        )
    )
    untrusted_policy_reference = (
        user_references_untrusted_policy(
            state.get(
                "user_message",
                "",
        )
    )
)
    if insufficient:

        return {
            "answer": (
                "The supplied Aster & Row documentation "
                "does not provide enough information to "
                "confirm this. I don't want to guess or "
                "make an unsupported certification claim. "
                "Please contact human support for confirmation."
        ),
            "sources": [],
            "handoff": True,
            "handoff_reason": (
                "The supplied documentation does not "
                "contain enough information."
        ),
    }

    conflict = state.get(
        "conflict_detected",
        False,
    )

    evidence = (
        format_retrieved_evidence(
            generation_passages
        )
    )

    prompt = (
        KNOWLEDGE_PROMPT.format(
            system_rules=
                SYSTEM_RULES,

            user_message=
                state.get(
                    "user_message",
                    "",
                ),
            review_required=state.get(
                "review_required",
                False,
            untrusted_policy_reference=
                untrusted_policy_reference,
),

            evidence=evidence,

            conflict_detected=
                conflict,

            insufficient_information=
                insufficient,
        )
    )

    llm = create_llm()

    response = llm.invoke(
        prompt
    )

    answer = (
        response.content
        .strip()
    )
    if insufficient:
        sources = []
    else:
        sources = extract_sources(
            generation_passages
    )

    review_required = state.get(
        "review_required",
        False,
)
    handoff = (
        conflict
        or insufficient
    )

    handoff_reason = None

    if conflict:

        handoff_reason = (
            "Current authoritative "
            "documents conflict."
        )

    elif insufficient:

        handoff_reason = (
            "The supplied documentation "
            "does not contain enough "
            "information."
        )
    elif review_required:

        handoff_reason = (
            "The policy requires human review "
            "before a resolution can be approved."
    )
    #print("\n[DEBUG] Calling Ollama...")
    #print(f"[DEBUG] Evidence chunks: {len(generation_passages)}")
    #print(f"[DEBUG] Prompt characters: {len(prompt)}")

    response = llm.invoke(prompt)

    #print("[DEBUG] Ollama response received.")
    return {
        "answer":
            answer,

        "sources":
            sources,

        "handoff":
            handoff,

        "handoff_reason":
            handoff_reason,
    }
def user_references_untrusted_policy(
    message: str,
) -> bool:
    """
    Detect when the user asks us to use known non-authoritative
    migration/internal material as company policy.
    """

    lowered = message.lower()

    references_internal = any(
        phrase in lowered
        for phrase in (
            "migration note",
            "migration document",
            "migration scratchpad",
            "internal note",
            "internal document",
        )
    )

    instruction_like = any(
        phrase in lowered
        for phrase in (
            "ignore the real policy",
            "ignore policy",
            "use that newer document",
            "approve my return",
            "ignore prior",
        )
    )

    return (
        references_internal
        and instruction_like
    )
def order_answer_node(
    state: AgentState,
) -> dict:

    if not state.get(
        "tool_called",
        False,
    ):
        return {}

    result = state.get(
        "order_result"
    )

    if not result:
        return {
            "answer": (
                "I couldn't retrieve order information."
            ),
            "handoff": True,
            "handoff_reason": (
                "Order lookup failed."
            ),
        }

    # --------------------------------------------------
    # Lookup failed
    # --------------------------------------------------

    if not result.get("found"):

        return {
            "answer": result.get(
                "message",
                "I couldn't find that order.",
            ),
            "handoff": (
                result.get("reason")
                == "order_not_found"
            ),
            "handoff_reason": (
                "Order could not be found."
                if result.get("reason")
                == "order_not_found"
                else None
            ),
        }

    order_id = result.get(
        "order_id",
        state.get("requested_order_id"),
    )

    status = str(
        result.get("status", "")
    ).strip().lower()

    # --------------------------------------------------
    # Cancelled
    # --------------------------------------------------

    if status == "cancelled":

        return {
            "answer": (
                f"Order {order_id} is cancelled "
                "and will not be shipped."
            )
        }

    # --------------------------------------------------
    # Returned
    # --------------------------------------------------

    if status == "returned":

        return {
            "answer": (
                f"Order {order_id} has been returned."
            )
        }

    # --------------------------------------------------
    # Delivered
    # --------------------------------------------------

    if status == "delivered":

        delivered_at = result.get(
            "delivered_at"
        )

        answer = (
            f"Order {order_id} has been delivered."
        )

        if delivered_at:
            answer += (
                f" It was delivered on "
                f"{delivered_at}."
            )

        return {
            "answer": answer
        }

    # --------------------------------------------------
    # Shipped
    # --------------------------------------------------

    if status == "shipped":

        carrier = result.get(
            "carrier"
        )

        tracking = result.get(
            "tracking_number"
        )

        eta = result.get(
            "estimated_delivery"
        )

        answer = (
            f"Order {order_id} has been shipped"
        )

        if carrier:

            answer += (
                f" with {carrier}"
            )

        answer += "."

        if tracking:

            answer += (
                f" The tracking number is "
                f"{tracking}."
            )

        if eta:

            # Format YYYY-MM-DD as customer-friendly date.
            try:
                from datetime import datetime

                parsed = datetime.strptime(
                    str(eta),
                    "%Y-%m-%d",
                )

                formatted_eta = (
                    parsed.strftime(
                        "%B %d, %Y"
                    )
                    .replace(
                        " 0",
                        " ",
                    )
                )

            except (
                ValueError,
                TypeError,
            ):

                formatted_eta = str(
                    eta
                )

            answer += (
                f" The estimated delivery date "
                f"is {formatted_eta}."
            )

        else:

            answer += (
                " A delivery estimate is "
                "currently unavailable."
            )

        return {
            "answer": answer
        }

    # --------------------------------------------------
    # Other known states
    # --------------------------------------------------

    return {
        "answer": (
            f"Order {order_id} currently has "
            f"status: {status}."
        )
    }
def unsupported_action_retrieval_node(
    state: AgentState,
) -> dict:

    message = state.get(
        "user_message",
        "",
    )

    passages = retrieve(
        message,
        k=6,
    )

    generation_passages = (
        filter_generation_evidence(
            passages
        )
    )

    order_id = extract_order_id(
        message
    )

    order_result = None
    tool_called = False

    if order_id is not None:

        order_result = (
            lookup_order(
                order_id
            )
        )

        tool_called = True

    return {
        "retrieval_query":
            message,

        "retrieved_passages":
            passages,

        "sources":
            extract_sources(
                generation_passages
            ),

        "requested_order_id":
            order_id,

        "order_result":
            order_result,

        "tool_called":
            tool_called,
    }
def unsupported_action_answer_node(
    state: AgentState,
) -> dict:

    passages = (
        filter_generation_evidence(
            state.get(
                "retrieved_passages",
                [],
            )
        )
    )

    evidence = (
        format_retrieved_evidence(
            passages
        )
    )

    order_result = (
        state.get(
            "order_result"
        )
    )

    prompt = (
        UNSUPPORTED_ACTION_PROMPT.format(
            system_rules=
                SYSTEM_RULES,

            user_message=
                state.get(
                    "user_message",
                    "",
                ),

            evidence=
                evidence,

            order_result=
                json.dumps(
                    order_result,
                    indent=2,
                    default=str,
                )
                if order_result
                else "NO ORDER LOOKUP RESULT",
        )
    )

    llm = create_llm()

    response = llm.invoke(
        prompt
    )

    return {
        "answer":
            response.content.strip(),

        "sources":
            extract_sources(
                passages
            ),

        "handoff":
            True,

        "handoff_reason":
            (
                "Requested action is not "
                "supported by this application."
            ),
    }
def update_history_node(
    state: AgentState,
) -> dict:

    history = list(
        state.get(
            "history",
            [],
        )
    )

    user_message = state.get(
        "user_message",
        "",
    )

    answer = state.get(
        "answer",
        "",
    )

    if user_message:

        history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

    if answer:

        history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    # Keep only recent context.
    history = history[-8:]

    return {
        "history": history,
    }
def update_topic_node(
    state: AgentState,
) -> dict:

    route = state.get(
        "route"
    )

    if route == "order":

        return {
            "current_topic": "order_status",
        }

    if route == "knowledge":

        query = state.get(
            "retrieval_query",
            "",
        )

        return {
            "current_topic": query[:200],
        }

    return {}
def after_safety(
    state: AgentState,
) -> str:

    if state.get(
        "blocked",
        False,
    ):

        return "blocked"

    return "continue"


def choose_route(
    state: AgentState,
) -> str:

    return state.get(
        "route",
        "knowledge",
    )