import json
import re
from pathlib import Path
from typing import Any

from app.config import DATA_DIR


ORDERS_FILE = DATA_DIR / "orders.json"


# --------------------------------------------------
# Order ID helpers
# --------------------------------------------------

ORDER_ID_PATTERN = re.compile(
    r"^ORD-\d{4}$"
)


def normalize_order_id(
    order_id: str | None,
) -> str | None:
    """
    Normalize harmless order-ID differences.

    Examples:
    " ord-1007 " -> "ORD-1007"
    "ORD-1007"   -> "ORD-1007"
    """

    if order_id is None:
        return None

    normalized = order_id.strip().upper()

    if not normalized:
        return None

    return normalized


def is_valid_order_id(
    order_id: str,
) -> bool:
    """
    Validate the expected order-ID format.

    Expected:
    ORD-1234
    """

    return bool(
        ORDER_ID_PATTERN.fullmatch(order_id)
    )


# --------------------------------------------------
# Order file loading
# --------------------------------------------------

def load_orders() -> list[dict[str, Any]]:
    """
    Load order data from disk.

    This function is internal only.

    Raw order records should NEVER be returned
    directly to the LLM.
    """

    if not ORDERS_FILE.exists():
        raise FileNotFoundError(
            f"Orders file not found: {ORDERS_FILE}"
        )

    with ORDERS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    # Support either:
    # [
    #   {...}
    # ]
    #
    # or:
    #
    # {
    #   "orders": [...]
    # }

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        orders = data.get("orders")

        if isinstance(orders, list):
            return orders

    raise ValueError(
        "orders.json has an unsupported structure."
    )


# --------------------------------------------------
# Safe field extraction helpers
# --------------------------------------------------

def get_first_available(
    order: dict[str, Any],
    *keys: str,
) -> Any:
    """
    Return the first matching top-level field.
    """

    for key in keys:

        value = order.get(key)

        if value not in (
            None,
            "",
        ):
            return value

    return None


def sanitize_order(
    order: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert a raw order record into a customer-safe
    representation.

    IMPORTANT:
    Never copy customer/internal dictionaries wholesale.
    """

    order_id = get_first_available(
        order,
        "order_id",
        "id",
    )

    status = get_first_available(
        order,
        "status",
    )

    if isinstance(status, str):
        status = status.strip().lower()

    result: dict[str, Any] = {
        "found": True,
        "order_id": order_id,
        "status": status,
    }

    # --------------------------------------------------
    # Cancelled orders
    # --------------------------------------------------

    if status == "cancelled":

        result["message"] = (
            "This order is cancelled and will not "
            "be shipped."
        )

        # Intentionally do NOT return:
        # estimated_delivery
        # tracking
        # carrier
        # stale delivery data

        return result

    # --------------------------------------------------
    # Returned orders
    # --------------------------------------------------

    if status == "returned":

        result["message"] = (
            "This order has been returned."
        )

        # Delivery/tracking information may now be stale.

        return result

    # --------------------------------------------------
    # Shipped / in-transit orders
    # --------------------------------------------------

    carrier = get_first_available(
        order,
        "carrier",
    )

    tracking_number = get_first_available(
        order,
        "tracking_number",
        "tracking",
    )

    estimated_delivery = get_first_available(
        order,
        "estimated_delivery",
        "delivery_estimate",
        "estimated_delivery_date",
    )

    if carrier is not None:
        result["carrier"] = carrier

    if tracking_number is not None:
        result["tracking_number"] = tracking_number

    if estimated_delivery is not None:
        result["estimated_delivery"] = (
            estimated_delivery
        )

    # --------------------------------------------------
    # Other safe fields
    # --------------------------------------------------

    shipped_at = get_first_available(
        order,
        "shipped_at",
        "shipped_date",
    )

    delivered_at = get_first_available(
        order,
        "delivered_at",
        "delivered_date",
    )

    if shipped_at is not None:
        result["shipped_at"] = shipped_at

    if delivered_at is not None:
        result["delivered_at"] = delivered_at

    return result


# --------------------------------------------------
# Lookup
# --------------------------------------------------

def find_order(
    normalized_order_id: str,
) -> dict[str, Any] | None:
    """
    Find one exact order.

    This function returns raw data internally,
    but its output must always pass through
    sanitize_order before leaving the tool.
    """

    orders = load_orders()

    for order in orders:

        raw_id = get_first_available(
            order,
            "order_id",
            "id",
        )

        if raw_id is None:
            continue

        candidate = normalize_order_id(
            str(raw_id)
        )

        if candidate == normalized_order_id:
            return order

    return None


# --------------------------------------------------
# Public tool API
# --------------------------------------------------

def lookup_order(
    order_id: str | None,
) -> dict[str, Any]:
    """
    Customer-safe order lookup.

    This is the ONLY function the future agent
    should call.
    """

    normalized = normalize_order_id(
        order_id
    )

    # --------------------------------------------------
    # Missing ID
    # --------------------------------------------------

    if normalized is None:

        return {
            "found": False,
            "reason": "missing_order_id",
            "message": (
                "Please provide your order ID, "
                "for example ORD-1007."
            ),
        }

    # --------------------------------------------------
    # Malformed ID
    # --------------------------------------------------

    if not is_valid_order_id(
        normalized
    ):

        return {
            "found": False,
            "reason": "invalid_order_id",
            "order_id": normalized,
            "message": (
                "That order ID format does not look valid. "
                "Please provide an ID such as ORD-1007."
            ),
        }

    # --------------------------------------------------
    # Lookup
    # --------------------------------------------------

    raw_order = find_order(
        normalized
    )

    if raw_order is None:

        return {
            "found": False,
            "reason": "order_not_found",
            "order_id": normalized,
            "message": (
                f"I could not find order {normalized}. "
                "Please verify the order ID."
            ),
        }

    # --------------------------------------------------
    # Sanitize before returning
    # --------------------------------------------------

    result = sanitize_order(
        raw_order
    )

    # Make sure returned order ID is normalized
    result["order_id"] = normalized

    return result