from typing import Any


def format_retrieved_evidence(
    passages: list[dict[str, Any]],
) -> str:
    """
    Convert retrieved chunks into explicit,
    delimited evidence for Ollama.
    """

    if not passages:

        return "NO RELEVANT EVIDENCE WAS FOUND."

    sections = []

    for index, passage in enumerate(
        passages,
        start=1,
    ):

        metadata = passage.get(
            "metadata",
            {},
        )

        filename = metadata.get(
            "filename",
            "unknown"
        )

        heading = metadata.get(
            "heading",
            "Unknown section"
        )

        status = metadata.get(
            "status",
            "unknown"
        )

        authority = metadata.get(
            "policy_authority",
            "unknown"
        )

        audience = metadata.get(
            "audience",
            "unknown"
        )

        text = passage.get(
            "text",
            ""
        )

        sections.append(
            f"""
[Evidence {index}]
Filename: {filename}
Heading: {heading}
Status: {status}
Authority: {authority}
Audience: {audience}

{text}
""".strip()
        )

    return "\n\n---\n\n".join(
        sections
    )

def extract_sources(
    passages: list[
        dict[str, Any]
    ],
    max_sources: int = 3,
) -> list[dict[str, str]]:

    ordered = sorted(
        passages,
        key=lambda item:
            item.get(
                "final_score",
                0,
            ),
        reverse=True,
    )

    sources = []
    seen = set()

    for passage in ordered:

        metadata = (
            passage.get(
                "metadata",
                {},
            )
        )

        if (
            metadata.get(
                "audience"
            )
            == "internal"
        ):
            continue

        if (
            metadata.get(
                "status"
            )
            != "active"
        ):
            continue

        filename = (
            metadata.get(
                "filename"
            )
        )

        heading = (
            metadata.get(
                "heading"
            )
            or "Document"
        )

        if not filename:
            continue

        key = (
            filename,
            heading,
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "filename":
                    filename,

                "heading":
                    heading,
            }
        )

        if (
            len(sources)
            >= max_sources
        ):
            break

    return sources