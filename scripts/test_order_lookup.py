from app.tools.order_lookup import (
    lookup_order,
)


def run_case(
    label: str,
    order_id,
):

    print("\n" + "=" * 70)

    print(label)

    print(
        f"Input: {repr(order_id)}"
    )

    result = lookup_order(
        order_id
    )

    print("Result:")

    for key, value in result.items():
        print(
            f"  {key}: {value}"
        )


def main():

    run_case(
        "Normal order lookup",
        "ORD-1007",
    )

    run_case(
        "Lowercase order ID",
        "ord-1007",
    )

    run_case(
        "Whitespace normalization",
        "   ORD-1007   ",
    )

    run_case(
        "Missing order ID",
        None,
    )

    run_case(
        "Empty order ID",
        "   ",
    )

    run_case(
        "Malformed order ID",
        "1007",
    )

    run_case(
        "Unknown order ID",
        "ORD-9999",
    )

    run_case(
        "Cancelled order",
        "ORD-1004",
    )

    run_case(
        "Missing ETA order",
        "ORD-1011",
    )


if __name__ == "__main__":
    main()