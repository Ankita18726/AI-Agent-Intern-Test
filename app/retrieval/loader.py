from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REQUIRED_METADATA = [
    "document_id",
    "title",
    "status",
    "effective_date",
    "audience",
    "policy_authority",
]
@dataclass
class LoadedDocument:
    """
    Represents one Markdown document after parsing.
    """

    filename: str
    path: str
    content: str
    metadata: dict[str, Any]

def validate_document_metadata(
    document: LoadedDocument,
) -> None:
    """
    Validate required front matter fields.
    """

    missing = [
        field
        for field in REQUIRED_METADATA
        if field not in document.metadata
    ]

    if missing:
        raise ValueError(
            f"{document.filename} is missing metadata: "
            f"{missing}"
        )
def parse_markdown_file(path: Path) -> LoadedDocument:
    """
    Read a Markdown file and separate YAML front matter
    from the Markdown body.
    """

    text = path.read_text(
        encoding="utf-8"
    )

    metadata: dict[str, Any] = {}
    content = text

    # --------------------------------------------------
    # Front matter must start with ---
    # --------------------------------------------------

    if text.startswith("---"):
        parts = text.split(
            "---",
            2
        )

        if len(parts) == 3:
            front_matter = parts[1]
            content = parts[2].strip()

            parsed = yaml.safe_load(
                front_matter
            )

            if parsed:
                metadata = parsed

    # --------------------------------------------------
    # Add filesystem metadata
    # --------------------------------------------------

    metadata["filename"] = path.name
    metadata["source_path"] = str(path)

    return LoadedDocument(
        filename=path.name,
        path=str(path),
        content=content,
        metadata=metadata,
    )


def load_knowledge_base(
    knowledge_base_dir: Path,
) -> list[LoadedDocument]:
    """
    Load every Markdown document from the knowledge base.
    """

    if not knowledge_base_dir.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: "
            f"{knowledge_base_dir}"
        )

    files = sorted(
        knowledge_base_dir.glob("*.md")
    )

    if not files:
        raise ValueError(
            f"No Markdown files found in "
            f"{knowledge_base_dir}"
        )

    documents = []

    for path in files:
        document = parse_markdown_file(path)
        documents.append(document)

    return documents