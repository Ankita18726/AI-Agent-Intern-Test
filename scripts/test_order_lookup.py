from app.tools.order_lookup import (
    extract_order_id,
    lookup_order,
)


def main():

    queries = [
        "Where is ORD-1007?",
        "Can you check ord-1007 please?",
        "Where is ORD-9999?",
        "Where is my order?",
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        order_id = extract_order_id(query)

        print(f"Extracted ID: {order_id}")

        result = lookup_order(order_id)

        print("Result:")
        print(result)


if __name__ == "__main__":
    main()