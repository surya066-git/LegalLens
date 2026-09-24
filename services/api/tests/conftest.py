from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings


@pytest.fixture
def storage_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("RATE_LIMIT_UPLOAD_PER_MINUTE", "10000")
    monkeypatch.setenv("RATE_LIMIT_QUESTION_PER_MINUTE", "10000")
    monkeypatch.setenv("GEMINI_API_KEYS", "")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()


@pytest.fixture
def client(storage_dir):
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()
