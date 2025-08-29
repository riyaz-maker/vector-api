import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.config import settings

@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_cohere_client():
    with patch('app.utils.cohere_client.cohere_client') as mock:
        mock.get_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 64   # 320 dim vector
        mock.health_check.return_value = True
        yield mock

@pytest.fixture
def sample_library_data():
    return {
        "name": "Test Library",
        "metadata": {
            "description": "Test library for unit tests",
            "category": "test"
        }
    }

@pytest.fixture
def sample_document_data():
    return {
        "name": "Test Document",
        "metadata": {
            "source": "test",
            "author": "tester"
        }
    }

@pytest.fixture
def sample_chunk_data():
    return {
        "text": "Test chunk for unit testing",
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 64,
        "metadata": {
            "source": "test",
            "page": 1
        }
    }

@pytest.fixture
def sample_search_data():
    return {
        "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 64,
        "k": 5,
        "metadata_filter": {
            "source": "test"
        }
    }
