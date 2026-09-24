from __future__ import annotations

from app.config import get_settings
from tests.helpers import employment_pdf, pdf_bytes_from_text, upload_file_tuple


def test_valid_pdf_upload(client):
    response = client.post("/documents", files=upload_file_tuple("offer-letter.pdf", employment_pdf()))
    assert response.status_code == 200
    data = response.json()
    assert data["documentId"].startswith("doc_")
    assert data["originalFilename"] == "offer-letter.pdf"
    assert data["storedFilename"] == "source.pdf"
    assert data["status"] == "uploaded"
    assert data["pageCount"] >= 1


def test_empty_pdf(client):
    response = client.post("/documents", files=upload_file_tuple("empty.pdf", b""))
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "empty_file"


def test_corrupt_pdf(client):
    response = client.post("/documents", files=upload_file_tuple("corrupt.pdf", b"%PDF-1.4\nnot a real pdf"))
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "malformed_pdf"


def test_fake_pdf_extension(client):
    response = client.post(
        "/documents",
        files=upload_file_tuple("fake.pdf", b"This is not a PDF", "application/pdf"),
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "malformed_pdf"


def test_oversized_pdf(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("MAX_PDF_UPLOAD_BYTES", "1024")
    monkeypatch.setenv("RATE_LIMIT_UPLOAD_PER_MINUTE", "10000")
    get_settings.cache_clear()
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        response = client.post("/documents", files=upload_file_tuple("large.pdf", b"x" * 2048, "application/pdf"))
        assert response.status_code == 413
        assert response.json()["detail"]["code"] == "file_too_large"
    get_settings.cache_clear()


def test_unsupported_extension(client):
    response = client.post(
        "/documents",
        files=upload_file_tuple("notes.txt", b"hello", "text/plain"),
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_file_extension"


def test_missing_file(client):
    response = client.post("/documents")
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_malicious_filename(client):
    data = employment_pdf()
    response = client.post("/documents", files=upload_file_tuple("$$bad$$.pdf", data))
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_filename"


def test_path_traversal_filename(client):
    data = employment_pdf()
    response = client.post("/documents", files={"file": ("../secret.pdf", data, "application/pdf")})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "unsafe_filename"


def test_wrong_content_type(client):
    response = client.post(
        "/documents",
        files=upload_file_tuple("offer.pdf", employment_pdf(), "image/png"),
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_content_type"
