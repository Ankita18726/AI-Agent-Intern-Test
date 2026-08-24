from typing import Any

from app.retrieval.index import create_vector_store
from app.retrieval.ranking import (
    calculate_precedence_score,
)


def retrieve(
    query: str,
    k: int = 8,
) -> list[dict[str, Any]]:
    """
    Retrieve semantically relevant chunks and apply
    deterministic document-precedence ranking.
    """

    vector_store = create_vector_store()

    results = vector_store.similarity_search_with_score(
        query,
        k=k,
    )

    retrieved = []

    for document, distance in results:

        metadata = document.metadata

        precedence = calculate_precedence_score(
            metadata
        )

        # Chroma similarity_score is actually a distance.
        # Lower distance means more similar.
        #
        # Convert it into a rough relevance value
        # where larger is better.
        semantic_relevance = 1.0 / (
            1.0 + float(distance)
        )

        final_score = (
            semantic_relevance
            + 0.25 * precedence
        )

        retrieved.append(
            {
                "text": document.page_content,
                "metadata": metadata,
                "semantic_score": semantic_relevance,
                "precedence_score": precedence,
                "final_score": final_score,
            }
        )

    retrieved.sort(
        key=lambda item: item["final_score"],
        reverse=True,
    )

    return retrieved