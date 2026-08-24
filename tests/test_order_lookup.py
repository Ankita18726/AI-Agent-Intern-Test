from app.tools.order_lookup import (
    is_valid_order_id,
    lookup_order,
    normalize_order_id,
)


def test_normalize_lowercase_order_id():

    assert (
        normalize_order_id(
            "ord-1007"
        )
        == "ORD-1007"
    )


def test_normalize_whitespace():

    assert (
        normalize_order_id(
            "   ORD-1007   "
        )
        == "ORD-1007"
    )


def test_empty_order_id():

    assert (
        normalize_order_id(
            "    "
        )
        is None
    )


def test_valid_order_id():

    assert is_valid_order_id(
        "ORD-1007"
    )


def test_invalid_order_id_missing_prefix():

    assert not is_valid_order_id(
        "1007"
    )


def test_invalid_order_id_bad_format():

    assert not is_valid_order_id(
        "ORDER-1007"
    )


def test_missing_order_id():

    result = lookup_order(
        None
    )

    assert result["found"] is False

    assert (
        result["reason"]
        == "missing_order_id"
    )


def test_invalid_order_id():

    result = lookup_order(
        "1007"
    )

    assert result["found"] is False

    assert (
        result["reason"]
        == "invalid_order_id"
    )


def test_unknown_order():

    result = lookup_order(
        "ORD-9999"
    )

    assert result["found"] is False

    assert (
        result["reason"]
        == "order_not_found"
    )


def test_lowercase_lookup():

    result = lookup_order(
        "ord-1007"
    )

    assert result["found"] is True

    assert (
        result["order_id"]
        == "ORD-1007"
    )


def test_whitespace_lookup():

    result = lookup_order(
        "   ORD-1007   "
    )

    assert result["found"] is True

    assert (
        result["order_id"]
        == "ORD-1007"
    )


def test_order_result_does_not_expose_customer_data():

    result = lookup_order(
        "ORD-1007"
    )

    text = str(result).lower()

    forbidden = [
        "email",
        "shipping_address",
        "address",
        "customer",
        "risk_score",
        "warehouse_note",
        "internal",
        "support_tags",
    ]

    for field in forbidden:

        assert field not in text


def test_cancelled_order_does_not_return_eta():

    result = lookup_order(
        "ORD-1004"
    )

    if (
        result["found"]
        and result["status"]
        == "cancelled"
    ):

        assert (
            "estimated_delivery"
            not in result
        )

        assert (
            "tracking_number"
            not in result
        )


def test_returned_order_does_not_return_stale_delivery():

    # If your dataset has a known returned order,
    # replace this ID with that actual order.
    #
    # Otherwise this test can remain conditional
    # until you identify one.

    possible_ids = [
        "ORD-1001",
        "ORD-1002",
        "ORD-1003",
        "ORD-1005",
        "ORD-1006",
        "ORD-1008",
        "ORD-1009",
        "ORD-1010",
    ]

    for order_id in possible_ids:

        result = lookup_order(
            order_id
        )

        if (
            result.get("found")
            and result.get("status")
            == "returned"
        ):

            assert (
                "estimated_delivery"
                not in result
            )

            assert (
                "tracking_number"
                not in result
            )

            return