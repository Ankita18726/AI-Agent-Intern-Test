from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.nodes import (
    after_safety,
    choose_route,
    initialize_turn,
    knowledge_answer_node,
    order_answer_node,
    order_lookup_node,
    retrieve_knowledge_node,
    route_node,
    safety_check_node,
    unsupported_action_answer_node,
    unsupported_action_retrieval_node,
    update_history_node,
    update_topic_node,
)
from app.agent.state import AgentState


def build_graph():
    """
    Construct and compile the Aster & Row agent.
    """

    workflow = StateGraph(
        AgentState
    )

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    workflow.add_node(
        "initialize",
        initialize_turn,
    )

    workflow.add_node(
        "safety",
        safety_check_node,
    )

    workflow.add_node(
        "router",
        route_node,
    )

    workflow.add_node(
        "retrieve_knowledge",
        retrieve_knowledge_node,
    )

    workflow.add_node(
        "knowledge_answer",
        knowledge_answer_node,
    )

    workflow.add_node(
        "order_lookup",
        order_lookup_node,
    )

    workflow.add_node(
        "order_answer",
        order_answer_node,
    )

    workflow.add_node(
        "unsupported_action_retrieval",
        unsupported_action_retrieval_node,
    )

    workflow.add_node(
        "unsupported_action_answer",
        unsupported_action_answer_node,
    )

    workflow.add_node(
        "update_topic",
        update_topic_node,
    )

    workflow.add_node(
        "update_history",
        update_history_node,
    )

    # --------------------------------------------------
    # Entry
    # --------------------------------------------------

    workflow.add_edge(
        START,
        "initialize",
    )

    workflow.add_edge(
        "initialize",
        "safety",
    )

    # --------------------------------------------------
    # Safety routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "safety",
        after_safety,
        {
            "blocked": "update_history",
            "continue": "router",
        },
    )

    # --------------------------------------------------
    # Intent routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "router",
        choose_route,
        {
            "knowledge": "retrieve_knowledge",
            "order": "order_lookup",
            "unsupported_action":
                "unsupported_action_retrieval",
            "blocked": "update_history",
        },
    )

    # --------------------------------------------------
    # Knowledge path
    # --------------------------------------------------

    workflow.add_edge(
        "retrieve_knowledge",
        "knowledge_answer",
    )

    workflow.add_edge(
        "knowledge_answer",
        "update_topic",
    )

    # --------------------------------------------------
    # Order path
    # --------------------------------------------------

    workflow.add_edge(
        "order_lookup",
        "order_answer",
    )

    workflow.add_edge(
        "order_answer",
        "update_topic",
    )

    # --------------------------------------------------
    # Unsupported action path
    # --------------------------------------------------

    workflow.add_edge(
        "unsupported_action_retrieval",
        "unsupported_action_answer",
    )

    workflow.add_edge(
        "unsupported_action_answer",
        "update_topic",
    )

    # --------------------------------------------------
    # Finalization
    # --------------------------------------------------

    workflow.add_edge(
        "update_topic",
        "update_history",
    )

    workflow.add_edge(
        "update_history",
        END,
    )

    # --------------------------------------------------
    # Short-term session memory
    # --------------------------------------------------

    checkpointer = InMemorySaver()

    return workflow.compile(
        checkpointer=checkpointer
    )


graph = build_graph()