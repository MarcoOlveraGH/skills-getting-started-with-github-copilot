"""Shared test fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for testing FastAPI endpoints.
    
    This fixture creates a fresh TestClient for each test,
    using the FastAPI app instance.
    """
    return TestClient(app)
