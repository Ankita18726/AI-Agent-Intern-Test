from uuid import uuid4

from app.agent.graph import graph


class SupportAgent:
    """
    Small wrapper around the LangGraph workflow.
    """

    def __init__(
        self,
        session_id: str | None = None,
    ):

        self.session_id = (
            session_id
            or str(uuid4())
        )

    def ask(
        self,
        message: str,
    ) -> dict:

        config = {
            "configurable": {
                "thread_id": self.session_id,
            }
        }

        result = graph.invoke(
            {
                "user_message": message,
            },
            config=config,
        )

        return result