from app.agent.service import SupportAgent


def print_sources(
    sources: list[dict],
):

    if not sources:
        return

    print("\nSources:")

    for source in sources:

        filename = source.get(
            "filename",
            "Unknown"
        )

        heading = source.get(
            "heading",
            "Document"
        )

        print(
            f"- {filename} — {heading}"
        )


def main():

    print("=" * 70)
    print("Aster & Row Support Agent")
    print("=" * 70)

    print(
        "Local LLM: Ollama"
    )

    print(
        "Type 'exit' to quit."
    )

    print()

    agent = SupportAgent()

    while True:

        try:

            user_input = input(
                "You: "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):

            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit",
        }:

            print("Goodbye!")
            break

        try:

            result = agent.ask(
                user_input
            )

            print()

            print(
                "Agent:",
                result.get(
                    "answer",
                    "I couldn't generate a response.",
                )
            )

            print_sources(
                result.get(
                    "sources",
                    [],
                )
            )

            if result.get(
                "handoff"
            ):

                print(
                    "\n⚠ Human assistance recommended"
                )

                reason = result.get(
                    "handoff_reason"
                )

                if reason:

                    print(
                        f"Reason: {reason}"
                    )

            print()

        except Exception as exc:

            print(
                f"\nError: {exc}\n"
            )


if __name__ == "__main__":
    main()