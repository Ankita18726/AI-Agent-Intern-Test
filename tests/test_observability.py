from app.observability.sanitizer import (
    sanitize_value,
)


def test_sanitizer_removes_sensitive_fields():

    raw = {
        "order_id":
            "ORD-1007",

        "status":
            "shipped",

        "customer_email":
            "private@example.test",

        "shipping_address":
            "123 Secret Street",

        "risk_score":
            91,

        "warehouse_note":
            "internal only",

        "carrier":
            "UPS",
    }

    sanitized = sanitize_value(
        raw
    )

    assert (
        sanitized[
            "order_id"
        ]
        == "ORD-1007"
    )

    assert (
        sanitized[
            "carrier"
        ]
        == "UPS"
    )

    assert (
        "customer_email"
        not in sanitized
    )

    assert (
        "shipping_address"
        not in sanitized
    )

    assert (
        "risk_score"
        not in sanitized
    )

    assert (
        "warehouse_note"
        not in sanitized
    )
def test_nested_sensitive_data_removed():

    raw = {
        "tool": {
            "result": {
                "order_id":
                    "ORD-1007",

                "customer": {
                    "email":
                        "secret@example.test",

                    "shipping_address":
                        "Secret address",
                },

                "internal": {
                    "risk_score":
                        88,

                    "warehouse_note":
                        "Do not disclose",
                },

                "status":
                    "shipped",
            }
        }
    }

    sanitized = sanitize_value(
        raw
    )

    text = str(
        sanitized
    ).lower()

    assert (
        "secret@example.test"
        not in text
    )

    assert (
        "secret address"
        not in text
    )

    assert (
        "risk_score"
        not in text
    )

    assert (
        "warehouse_note"
        not in text
    )

    assert (
        "shipped"
        in text
    )
from pathlib import Path

from app.observability.logger import (
    write_trace,
)


def test_trace_writer_does_not_raise():

    trace = {
        "session_id":
            "test",

        "user_message":
            "test message",

        "answer":
            "test answer",
    }

    write_trace(
        trace
    )
from app.agent.service import (
    SupportAgent,
)


def test_agent_returns_traceable_fields():

    agent = SupportAgent(
        session_id="trace-fields-test"
    )

    result = agent.ask(
        "Where is ORD-1007?"
    )

    assert (
        result[
            "route"
        ]
        == "order"
    )

    assert (
        result[
            "tool_called"
        ]
        is True
    )

    assert (
        result[
            "requested_order_id"
        ]
        == "ORD-1007"
    )

    assert (
        result[
            "order_result"
        ][
            "status"
        ]
        == "shipped"
    )