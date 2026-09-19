import pytest
from app.domain.document_models import StoredPage
from app.services.clause_detection import detect_clauses


def create_page(text: str, page_num: int = 1, start_offset: int = 0) -> StoredPage:
    return StoredPage(
        page_number=page_num,
        raw_text=text,
        normalized_text=text.lower(),
        extraction_method="mock",
        extraction_status="extracted",
        warnings=[],
        start_offset=start_offset,
        end_offset=start_offset + len(text)
    )


def test_detect_numbered_clauses():
    text = (
        "1. Definitions\n"
        "Here are some definitions.\n\n"
        "1.1 Sub definitions\n"
        "More text here.\n\n"
        "8.2 Termination\n"
        "Termination text.\n\n"
        "(a) Exceptions\n"
        "Exception text."
    )
    pages = [create_page(text)]
    clauses = detect_clauses(pages)
    
    assert len(clauses) == 4
    assert clauses[0].clause_number == "1"
    assert clauses[0].title == "Definitions"
    
    assert clauses[1].clause_number == "1.1"
    assert clauses[1].title == "Sub definitions"
    
    assert clauses[2].clause_number == "8.2"
    assert clauses[2].title == "Termination"
    
    assert clauses[3].clause_number == "(a)"
    assert clauses[3].title == "Exceptions"


def test_detect_unnumbered_clauses():
    text = (
        "Introduction\n"
        "This is an unnumbered section.\n\n"
        "Background\n"
        "Another unnumbered section.\n\n"
    )
    pages = [create_page(text)]
    clauses = detect_clauses(pages)
    
    assert len(clauses) == 2
    assert clauses[0].clause_number is None
    assert clauses[0].title == "Introduction"
    assert clauses[1].clause_number is None
    assert clauses[1].title == "Background"


def test_multipage_clause():
    page1_text = "1. Long Clause\nStart of clause on page 1.\n"
    page2_text = "End of clause on page 2.\n\n2. Next Clause\nNext clause."
    
    p1 = create_page(page1_text, 1, 0)
    p2 = create_page(page2_text, 2, len(page1_text) + 2)
    
    clauses = detect_clauses([p1, p2])
    
    assert len(clauses) == 2
    assert clauses[0].clause_number == "1"
    assert clauses[0].page_start == 1
    assert clauses[0].page_end == 2
    assert "Start of clause on page 1." in clauses[0].source_text
    assert "End of clause on page 2." in clauses[0].source_text
    
    assert clauses[1].clause_number == "2"
    assert clauses[1].page_start == 2
    assert clauses[1].page_end == 2
