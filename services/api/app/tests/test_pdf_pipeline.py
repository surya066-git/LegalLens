from collections.abc import Iterator

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.clause_detection import detect_clauses
from app.services.chunking import chunk_document
from app.services.pdf_processing import extract_pages


@pytest.fixture(autouse=True)
def isolated_storage(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Iterator[None]:
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path / "documents"))
    monkeypatch.setenv("MAX_PDF_UPLOAD_BYTES", "1000000")
    monkeypatch.setenv("MIN_EXTRACTABLE_TEXT_CHARS", "20")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def make_pdf(pages: list[str]) -> bytes:
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_textbox(
                pymupdf.Rect(72, 72, 520, 760),
                text,
                fontsize=11,
            )
    data = document.tobytes()
    document.close()
    return data


def upload_pdf(client: TestClient, data: bytes, filename: str = "offer-letter.pdf") -> dict:
    response = client.post(
        "/documents",
        files={"file": (filename, data, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def process_pdf(client: TestClient, document_id: str) -> dict:
    response = client.post(f"/documents/{document_id}/process")
    assert response.status_code == 200, response.text
    return response.json()


def test_valid_upload_processes_and_preserves_page_numbers(client: TestClient) -> None:
    upload = upload_pdf(client, make_pdf(["1 Definitions\nEmployment means service.", "2 Termination\nNotice is required."]))

    processed = process_pdf(client, upload["documentId"])
    pages_response = client.get(f"/documents/{upload['documentId']}/pages")

    assert processed["pageCount"] == 2
    assert pages_response.status_code == 200
    assert [page["pageNumber"] for page in pages_response.json()["pages"]] == [1, 2]
    assert pages_response.json()["pages"][0]["rawText"].startswith("1 Definitions")


def test_upload_rejects_invalid_content_type(client: TestClient) -> None:
    response = client.post(
        "/documents",
        files={"file": ("not-a-pdf.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] in {"invalid_file_extension", "invalid_content_type"}


def test_upload_rejects_malformed_pdf(client: TestClient) -> None:
    response = client.post(
        "/documents",
        files={"file": ("broken.pdf", b"%PDF-1.7 definitely not valid", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "malformed_pdf"


def test_upload_rejects_oversized_pdf(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_PDF_UPLOAD_BYTES", "10")
    get_settings.cache_clear()

    response = client.post(
        "/documents",
        files={"file": ("large.pdf", make_pdf(["1 Definitions\nEnough text for a PDF."]), "application/pdf")},
    )

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "file_too_large"


def test_upload_rejects_unsafe_filename(client: TestClient) -> None:
    response = client.post(
        "/documents",
        files={"file": ("../evil.pdf", make_pdf(["1 Safe\nText"]), "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "unsafe_filename"


def test_empty_page_is_marked_as_scanned_like(client: TestClient) -> None:
    upload = upload_pdf(client, make_pdf([""]))
    process_pdf(client, upload["documentId"])

    response = client.get(f"/documents/{upload['documentId']}/pages/1")

    assert response.status_code == 200
    page = response.json()
    assert page["pageNumber"] == 1
    assert page["extractionStatus"] == "empty"
    assert "OCR is not yet supported" in page["warnings"][0]


def test_clause_detection_preserves_real_numbers_and_parenthetical_numbers(tmp_path) -> None:
    pdf_path = tmp_path / "numbered.pdf"
    pdf_path.write_bytes(
        make_pdf(
            [
                "1 Definitions\nEmployment means service.\n1.1 Role\nThe role is Engineer.\n8.2 Non-compete\nThe employee shall not compete.\n(a) Exception\nThis applies where permitted."
            ]
        )
    )
    pages = extract_pages(pdf_path, get_settings())

    clauses = detect_clauses(pages)

    assert [clause.clause_number for clause in clauses] == ["1", "1.1", "8.2", "(a)"]
    assert clauses[2].source_text.startswith("8.2 Non-compete")


def test_unnumbered_heading_clause_uses_null_number(tmp_path) -> None:
    pdf_path = tmp_path / "unnumbered.pdf"
    pdf_path.write_bytes(make_pdf(["Confidentiality\nThe employee must keep company information private."]))
    pages = extract_pages(pdf_path, get_settings())

    clauses = detect_clauses(pages)

    assert len(clauses) == 1
    assert clauses[0].clause_number is None
    assert clauses[0].title == "Confidentiality"


def test_ambiguous_numbers_are_not_fabricated(tmp_path) -> None:
    pdf_path = tmp_path / "ambiguous.pdf"
    pdf_path.write_bytes(
        make_pdf(
            [
                "This paragraph mentions 8.2 but does not start a clause.\n5 days of notice may be required.\nThe date 2026 is not a clause number."
            ]
        )
    )
    pages = extract_pages(pdf_path, get_settings())

    clauses = detect_clauses(pages)

    assert clauses == []


def test_multi_page_clause_preserves_page_range(tmp_path) -> None:
    pdf_path = tmp_path / "multi-page.pdf"
    pdf_path.write_bytes(
        make_pdf(
            [
                "1 Confidentiality\nThe employee must keep information private.",
                "This obligation continues after employment.\n2 Termination\nEither party may give notice.",
            ]
        )
    )
    pages = extract_pages(pdf_path, get_settings())

    clauses = detect_clauses(pages)

    assert clauses[0].clause_number == "1"
    assert clauses[0].page_start == 1
    assert clauses[0].page_end == 2
    assert "This obligation continues" in clauses[0].source_text
    assert clauses[1].clause_number == "2"
    assert clauses[1].page_start == 2


def test_chunks_preserve_clause_source_text_without_normalizing_evidence(tmp_path) -> None:
    pdf_path = tmp_path / "chunks.pdf"
    pdf_path.write_bytes(make_pdf(["1 Definitions\nEmployment   means service.\n2 Term\nThe term is one year."]))
    pages = extract_pages(pdf_path, get_settings())
    clauses = detect_clauses(pages)

    chunks = chunk_document(pages, clauses)

    clause_chunks = [chunk for chunk in chunks if chunk.clause_id is not None]
    assert len(clause_chunks) == len(clauses)
    assert clause_chunks[0].source_text == clauses[0].source_text
    assert "Employment   means service" in clause_chunks[0].source_text
    assert clause_chunks[0].normalized_text != clause_chunks[0].source_text


def test_missing_document_ids_return_clear_errors(client: TestClient) -> None:
    missing_id = "doc_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

    status_response = client.get(f"/documents/{missing_id}")
    process_response = client.post(f"/documents/{missing_id}/process")

    assert status_response.status_code == 404
    assert status_response.json()["detail"]["code"] == "document_not_found"
    assert process_response.status_code == 404
    assert process_response.json()["detail"]["code"] == "document_not_found"
