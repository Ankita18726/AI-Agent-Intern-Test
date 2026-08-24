from app.config import (
    DATA_DIR,
    EVALUATION_DIR,
    KNOWLEDGE_BASE_DIR,
)


def test_knowledge_base_exists():
    assert KNOWLEDGE_BASE_DIR.exists()


def test_data_directory_exists():
    assert DATA_DIR.exists()


def test_evaluation_directory_exists():
    assert EVALUATION_DIR.exists()