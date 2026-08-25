import re
from typing import Any

from app.retrieval.index import create_vector_store
from app.retrieval.ranking import calculate_precedence_score


STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "do",
    "does",
    "did",
    "i",
    "you",
    "your",
    "my",
    "to",
    "of",
    "for",
    "in",
    "on",
    "and",
    "or",
    "it",
    "this",
    "that",
    "about",
    "can",
    "could",
    "would",
    "should",
    "have",
    "has",
    "with",
}


def tokenize(
    text: str,
) -> set[str]:

    words = re.findall(
        r"[a-z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if (
            word not in STOP_WORDS
            and len(word) > 2
        )
    }


def lexical_score(
    query: str,
    text: str,
    metadata: dict[str, Any],
) -> float:

    query_tokens = tokenize(
        query
    )

    if not query_tokens:
        return 0.0

    searchable = " ".join(
        [
            str(
                metadata.get(
                    "title",
                    "",
                )
            ),
            str(
                metadata.get(
                    "heading",
                    "",
                )
            ),
            text,
        ]
    )

    document_tokens = tokenize(
        searchable
    )

    overlap = (
        query_tokens
        & document_tokens
    )

    return (
        len(overlap)
        / len(query_tokens)
    )


def retrieve(
    query: str,
    k: int = 8,
) -> list[dict[str, Any]]:

    vector_store = (
        create_vector_store()
    )

    candidate_k = max(
        k * 2,
        12,
    )

    results = (
        vector_store
        .similarity_search_with_score(
            query,
            k=candidate_k,
        )
    )

    retrieved = []

    for document, distance in results:

        metadata = (
            document.metadata
        )

        semantic_relevance = (
            1.0
            / (
                1.0
                + float(distance)
            )
        )

        lexical_relevance = (
            lexical_score(
                query,
                document.page_content,
                metadata,
            )
        )

        precedence = (
            calculate_precedence_score(
                metadata
            )
        )

        final_score = (
            0.60
            * semantic_relevance
            +
            0.25
            * lexical_relevance
            +
            0.15
            * max(
                precedence,
                -2.0,
            )
        )

        retrieved.append(
            {
                "text":
                    document.page_content,

                "metadata":
                    metadata,

                "semantic_score":
                    semantic_relevance,

                "lexical_score":
                    lexical_relevance,

                "precedence_score":
                    precedence,

                "final_score":
                    final_score,
            }
        )

    retrieved.sort(
        key=lambda item:
            item["final_score"],
        reverse=True,
    )

    return retrieved[:k]