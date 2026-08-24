from app.config import KNOWLEDGE_BASE_DIR
from app.retrieval.loader import load_knowledge_base


def main():

    documents = load_knowledge_base(
        KNOWLEDGE_BASE_DIR
    )

    print(
        f"Loaded {len(documents)} documents\n"
    )

    for document in documents:

        print("=" * 70)

        print(
            f"Filename: {document.filename}"
        )

        print(
            f"Title: "
            f"{document.metadata.get('title')}"
        )

        print(
            f"Status: "
            f"{document.metadata.get('status')}"
        )

        print(
            f"Audience: "
            f"{document.metadata.get('audience')}"
        )

        print(
            f"Authority: "
            f"{document.metadata.get('policy_authority')}"
        )

        print(
            f"Document ID: "
            f"{document.metadata.get('document_id')}"
        )

        print(
            f"Characters: "
            f"{len(document.content)}"
        )


if __name__ == "__main__":
    main()