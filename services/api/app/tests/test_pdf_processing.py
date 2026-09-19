from unittest.mock import MagicMock, patch

import pytest
from app.config import get_settings
from app.services.pdf_processing import extract_pages


@pytest.fixture
def settings():
    return get_settings()


def test_extract_pages_valid(settings):
    mock_pdf = MagicMock()
    mock_pdf.page_count = 2
    
    mock_page_1 = MagicMock()
    mock_page_1.get_text.return_value = "1. Introduction\nThis is a standard contract with plenty of text."
    
    mock_page_2 = MagicMock()
    mock_page_2.get_text.return_value = "2. Salary\nThe salary is big."
    
    # Side effect returns page 1 then page 2
    mock_pdf.load_page.side_effect = [mock_page_1, mock_page_2]
    
    with patch("pymupdf.open", return_value=mock_pdf):
        pages = extract_pages("dummy.pdf", settings)
        
    assert len(pages) == 2
    assert pages[0].extraction_status == "extracted"
    assert pages[1].extraction_status == "extracted"
    assert "1. Introduction" in pages[0].raw_text


def test_extract_pages_empty(settings):
    mock_pdf = MagicMock()
    mock_pdf.page_count = 1
    
    mock_page_1 = MagicMock()
    mock_page_1.get_text.return_value = "   \n  "  # Just whitespace
    mock_pdf.load_page.return_value = mock_page_1
    
    with patch("pymupdf.open", return_value=mock_pdf):
        pages = extract_pages("dummy.pdf", settings)
        
    assert len(pages) == 1
    assert pages[0].extraction_status == "empty"
    assert "No extractable text" in pages[0].warnings[0]


def test_extract_pages_little_text(settings):
    mock_pdf = MagicMock()
    mock_pdf.page_count = 1
    
    mock_page_1 = MagicMock()
    mock_page_1.get_text.return_value = "Too short"
    mock_pdf.load_page.return_value = mock_page_1
    
    with patch("pymupdf.open", return_value=mock_pdf):
        pages = extract_pages("dummy.pdf", settings)
        
    assert len(pages) == 1
    assert pages[0].extraction_status == "potentially_scanned"
    assert "Little extractable text" in pages[0].warnings[0]
