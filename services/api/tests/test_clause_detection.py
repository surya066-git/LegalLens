from app.services.clause_detection import detect_clauses
from app.domain.document_models import StoredPage

def test_detect_clauses():
    page1 = StoredPage(
        page_number=1,
        raw_text="1.1 The employee will work 40 hours.\n2. Termination must have notice.",
        normalized_text="1.1 the employee will work 40 hours.\n2. termination must have notice.",
        extraction_method="test",
        extraction_status="extracted",
        warnings=[],
        start_offset=0,
        end_offset=100
    )
    pages = [page1]
    clauses = detect_clauses(pages)
    assert isinstance(clauses, list)
