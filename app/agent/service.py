import time
from uuid import uuid4

from app.agent.graph import graph
from app.config import DEBUG
from app.observability.logger import (
    build_turn_trace,
    write_trace,
)


class SupportAgent:
    """
    Small wrapper around the LangGraph workflow.

    A SupportAgent instance represents one conversation
    session/thread.
    """

    def __init__(
        self,
        session_id: str | None = None,
    ):

        self.session_id = (
            session_id
            or str(
                uuid4()
            )
        )

    def ask(
        self,
        message: str,
    ) -> dict:

        config = {
            "configurable": {
                "thread_id":
                    self.session_id,
            }
        }

        started = (
            time.perf_counter()
        )

        try:

            result = graph.invoke(
                {
                    "user_message":
                        message,
                },
                config=config,
            )

            duration_ms = (
                (
                    time.perf_counter()
                    - started
                )
                * 1000
            )

            trace = build_turn_trace(
                session_id=
                    self.session_id,

                user_message=
                    message,

                state=
                    result,

                duration_ms=
                    round(
                        duration_ms,
                        2,
                    ),

                error=None,
            )

            write_trace(
                trace
            )

            if DEBUG:

                self._print_debug(
                    result,
                    duration_ms,
                )

            return result

        except Exception as exc:

            duration_ms = (
                (
                    time.perf_counter()
                    - started
                )
                * 1000
            )

            error_text = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            trace = build_turn_trace(
                session_id=
                    self.session_id,

                user_message=
                    message,

                state={},

                duration_ms=
                    round(
                        duration_ms,
                        2,
                    ),

                error=
                    error_text,
            )

            write_trace(
                trace
            )

            raise

    def _print_debug(
        self,
        result: dict,
        duration_ms: float,
    ) -> None:

        print()
        print(
            "-" * 60
        )

        print(
            "[DEBUG TRACE]"
        )

        print(
            f"Session: "
            f"{self.session_id}"
        )

        print(
            f"Route: "
            f"{result.get('route')}"
        )

        print(
            f"Route reason: "
            f"{result.get('route_reason')}"
        )

        print(
            f"Tool called: "
            f"{result.get('tool_called', False)}"
        )

        print(
            f"Requested order ID: "
            f"{result.get('requested_order_id')}"
        )

        print(
            f"Retrieved passages: "
            f"{len(result.get('retrieved_passages', []))}"
        )

        print(
            f"Conflict: "
            f"{result.get('conflict_detected', False)}"
        )

        print(
            f"Insufficient: "
            f"{result.get('insufficient_information', False)}"
        )

        print(
            f"Review required: "
            f"{result.get('review_required', False)}"
        )

        print(
            f"Handoff: "
            f"{result.get('handoff', False)}"
        )

        print(
            f"Duration: "
            f"{duration_ms:.2f} ms"
        )

        print(
            "-" * 60
        )