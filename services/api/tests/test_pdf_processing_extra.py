from app.services.pdf_processing import process_pdf_document, extract_pages
from app.config import get_settings
from app.services.errors import raise_api_error
from fastapi import HTTPException
import pytest
from unittest.mock import patch

def test_extract_pages_no_file(tmp_path):
    settings = get_settings()
    pdf_path = tmp_path / "missing.pdf"
    with pytest.raises(HTTPException):
        extract_pages(pdf_path, settings)

@patch('app.services.pdf_processing.pymupdf.open')
def test_extract_pages_too_many(mock_open, tmp_path):
    mock_pdf = mock_open.return_value
    mock_pdf.page_count = 1000
    settings = get_settings()
    settings.max_pdf_pages = 10
    with pytest.raises(HTTPException):
        extract_pages(tmp_path / "test.pdf", settings)

def test_process_pdf_not_found(tmp_path):
    settings = get_settings()
    settings.document_storage_dir = tmp_path
    with pytest.raises(HTTPException):
        process_pdf_document("doc_missing", settings)
