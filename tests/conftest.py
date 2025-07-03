import pytest
import os
import yaml
from pathlib import Path
from typing import Dict, Any

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    config_path = Path("config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return path to test data directory."""
    return Path("test_docs")

@pytest.fixture(scope="session")
def sample_job() -> Dict[str, Any]:
    """Return a sample job description."""
    return {
        "title": "Machine Learning Engineer",
        "skills": [
            {"name": "Python", "level": "Expert", "years": 5},
            {"name": "PyTorch", "level": "Advanced", "years": 3},
            {"name": "TensorFlow", "level": "Advanced", "years": 3},
            {"name": "AWS", "level": "Intermediate", "years": 2}
        ],
        "certifications": [
            "AWS Machine Learning Specialty",
            "Google Cloud Professional ML Engineer"
        ],
        "experience": 5
    }

@pytest.fixture(scope="session")
def sample_profile() -> Dict[str, Any]:
    """Return a sample candidate profile."""
    return {
        "name": "John Doe",
        "title": "Senior ML Engineer",
        "skills": [
            {"name": "Python", "level": "Expert", "years": 8},
            {"name": "PyTorch", "level": "Expert", "years": 6},
            {"name": "TensorFlow", "level": "Advanced", "years": 4},
            {"name": "AWS", "level": "Advanced", "years": 5}
        ],
        "certifications": [
            "AWS Machine Learning Specialty",
            "Google Cloud Professional ML Engineer",
            "Deep Learning Specialization"
        ],
        "experience": 8
    }

@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory) -> Path:
    """Create a temporary directory for test files."""
    return tmp_path_factory.mktemp("test_files")

@pytest.fixture(scope="session")
def mock_document_processor():
    """Mock document processor for testing."""
    class MockDocumentProcessor:
        def process_document(self, file_path: str) -> Dict[str, Any]:
            return {
                "text": "Sample document text",
                "sections": {
                    "skills": ["Python", "PyTorch"],
                    "experience": "5 years",
                    "certifications": ["AWS ML"]
                }
            }
    return MockDocumentProcessor()

@pytest.fixture(scope="session")
def mock_matching_engine():
    """Mock matching engine for testing."""
    class MockMatchingEngine:
        def match_candidate(self, profile: Dict[str, Any], job: Dict[str, Any]) -> float:
            return 0.85
    return MockMatchingEngine()

@pytest.fixture(scope="session")
def mock_visualizer():
    """Mock visualizer for testing."""
    class MockVisualizer:
        def create_skill_heatmap(self, skills: list) -> None:
            pass
        def create_experience_timeline(self, skills: list) -> None:
            pass
    return MockVisualizer() 