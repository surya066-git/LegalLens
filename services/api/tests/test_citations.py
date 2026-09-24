from __future__ import annotations

from app.domain.document_models import StoredChunk
from app.domain.schemas import Citation, QuestionResponse
from app.services.citation_validation import CitationValidationService


def _chunk() -> StoredChunk:
    text = "Either party may terminate this agreement with 30 days written notice."
    return StoredChunk(
        chunk_id="chunk_1",
        clause_id="clause_1",
        clause_number="1",
        page_start=1,
        page_end=1,
        source_text=text,
        normalized_text=text.lower(),
        start_offset=0,
        end_offset=len(text),
    )


def _response(source_text: str) -> QuestionResponse:
    return QuestionResponse(
        status="LLM_SUCCESS",
        answer_type="DIRECTLY_ANSWERED",
        answer="The notice period is 30 days.",
        confidence="high",
        citations=[Citation(page=9, clause_number="99", source_text=source_text, chunk_id=None)],
        ambiguities=[],
        lawyer_questions=[],
        disclaimer="This is legal information, not legal advice. Consult a qualified lawyer.",
    )


def test_valid_citation_rewritten_from_chunk():
    result = CitationValidationService().validate_citations(_response("30 days written notice"), [_chunk()])
    assert result.citations
    assert result.citations[0].page == 1
    assert result.citations[0].clause_number == "1"
    assert result.citations[0].chunk_id == "chunk_1"


def test_invalid_citation_rejected():
    result = CitationValidationService().validate_citations(
        _response("The employee is entitled to unlimited vacation under the Mars Employment Act."),
        [_chunk()],
    )
    assert result.status == "CITATION_VALIDATION_FAILED"
    assert result.answer_type == "NOT_FOUND"
    assert result.citations == []
