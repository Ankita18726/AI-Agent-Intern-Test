from app.retrieval.retriever import retrieve


def run_query(query: str):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = retrieve(query, k=5)

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"\n[{index}] {metadata.get('filename')}")
        print(f"Heading: {metadata.get('heading')}")
        print(f"Status: {metadata.get('status')}")
        print(
            f"Authority: "
            f"{metadata.get('policy_authority')}"
        )

        print(
            f"Semantic score: "
            f"{result.get('semantic_score', 0):.4f}"
        )

        print(
            f"Precedence score: "
            f"{result.get('precedence_score', 0):.4f}"
        )

        print(
            f"Final score: "
            f"{result.get('final_score', 0):.4f}"
        )

        print("\nText:")
        print(result["text"][:350])


def main():
    queries = [
        "How long do I have to return an unused backpack?",
        "Do you ship to Canada?",
        "What is the warranty for drinkware?",
        "Can I put the Breeze Tumbler in the dishwasher?",
        "Tell me about the old 45 day return policy.",
    ]

    for query in queries:
        run_query(query)


if __name__ == "__main__":
    main()