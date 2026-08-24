from dataclasses import dataclass
from typing import Any

from app.retrieval.loader import LoadedDocument


@dataclass
class DocumentChunk:
    """
    A searchable semantic section of a document.
    """

    chunk_id: str
    text: str
    metadata: dict[str, Any]


def split_by_headings(
    document: LoadedDocument,
) -> list[DocumentChunk]:
    """
    Split Markdown content into sections based on
    Markdown headings.
    """

    lines = document.content.splitlines()

    sections = []

    current_heading = None
    current_level = None
    current_lines = []

    for line in lines:

        stripped = line.strip()

        # --------------------------------------------------
        # Detect Markdown heading
        # --------------------------------------------------

        if stripped.startswith("#"):

            heading_marker = stripped.split(
                " ",
                1
            )[0]

            heading_level = len(
                heading_marker
            )

            heading_text = stripped[
                heading_level:
            ].strip()

            # Save previous section
            if current_lines:

                sections.append(
                    (
                        current_heading,
                        current_level,
                        current_lines,
                    )
                )

            current_heading = heading_text
            current_level = heading_level
            current_lines = []

        else:
            current_lines.append(line)

    # Save final section
    if current_lines:

        sections.append(
            (
                current_heading,
                current_level,
                current_lines,
            )
        )

    chunks = []

    for index, (
        heading,
        level,
        section_lines,
    ) in enumerate(sections):

        
        body = "\n".join(
            section_lines
        ).strip()

        if heading:
            text = (
                f"Document: {document.metadata['title']}\n"
                f"Section: {heading}\n\n"
                f"{body}"
            )
        else:
            text = body

        if not text:
            continue

        metadata = dict(
            document.metadata
        )

        metadata["heading"] = heading
        metadata["heading_level"] = level
        metadata["chunk_index"] = index

        chunk_id = (
            f"{document.metadata['document_id']}"
            f"-chunk-{index}"
        )

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                metadata=metadata,
            )
        )

    return chunks


def chunk_documents(
    documents: list[LoadedDocument],
) -> list[DocumentChunk]:

    chunks = []

    for document in documents:

        document_chunks = split_by_headings(
            document
        )

        chunks.extend(
            document_chunks
        )

    return chunks