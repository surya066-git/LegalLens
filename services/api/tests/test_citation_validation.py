from app.services.citation_validation import CitationValidationService
from app.domain.schemas import QuestionResponse, Citation
from app.domain.document_models import StoredChunk

def test_citation_validation():
    service = CitationValidationService()
    chunk = StoredChunk(
        chunk_id="c1",
        document_id="d1",
        clause_id="clause1",
        clause_number="1.1",
        source_text="This is the source chunk.",
        normalized_text="this is the source chunk",
        page_start=1,
        page_end=1,
        start_offset=0,
        end_offset=50,
        token_count=10
    )
    
    response = QuestionResponse(
        status="ANSWERED",
        answer_type="DIRECTLY_ANSWERED",
        answer="An answer.",
        confidence="high",
        missing_information=[],
        citations=[
            Citation(
                page=1,
                clause_number="1.1",
                source_text="This is the source chunk.",
                chunk_id="c1"
            )
        ],
        ambiguities=[],
        lawyer_questions=[],
        disclaimer="Disclaimer"
    )
    
    validated = service.validate_citations(response, [chunk])
    assert validated.status != "CITATION_VALIDATION_FAILED"
    assert len(validated.citations) == 1
    
    # Test failure
    bad_response = response.model_copy(deep=True)
    bad_response.citations[0].source_text = "Completely different text."
    validated_bad = service.validate_citations(bad_response, [chunk])
    assert len(validated_bad.citations) == 0
