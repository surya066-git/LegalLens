from app.services.chunking import chunk_document
from app.domain.document_models import StoredPage, StoredClause

def test_chunk_document():
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
    clause1 = StoredClause(
        clause_id="c1",
        clause_number="1.1",
        title="Title",
        page_start=1,
        page_end=1,
        source_text="1.1 The employee will work 40 hours.",
        start_offset=0,
        end_offset=50
    )
    chunks = chunk_document([page1], [clause1])
    assert len(chunks) > 0
