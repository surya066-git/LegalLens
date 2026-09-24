from __future__ import annotations

from app.domain.document_models import StoredChunk
from app.services.retrieval import RetrievalService


def _chunk(chunk_id: str, text: str, clause: str | None = None, page: int = 1) -> StoredChunk:
    return StoredChunk(
        chunk_id=chunk_id,
        clause_id=f"clause_{chunk_id}",
        clause_number=clause,
        page_start=page,
        page_end=page,
        source_text=text,
        normalized_text=text.lower(),
        start_offset=0,
        end_offset=len(text),
    )


CHUNKS = [
    _chunk("1", "Either party may terminate this agreement with 30 days written notice unless another period is expressly required by applicable policy or law.", "1", 1),
    _chunk("2", "The employee shall serve a probationary period of six months from the commencement date.", "2", 1),
    _chunk("3", "The employee will receive an annual salary of 90,000 USD, payable monthly.", "3", 1),
    _chunk("4", "The employee shall not join a competing business within 6 months after termination.", "5", 2),
    _chunk("5", "Normal working hours are 9:00 to 17:30 Monday to Friday.", "6", 2),
]


def test_exact_phrase_retrieval():
    results = RetrievalService().retrieve_chunks("30 days written notice", CHUNKS, top_k=3)
    assert results
    assert "30 days" in results[0].source_text


def test_synonym_retrieval():
    results = RetrievalService().retrieve_chunks("What is the compensation?", CHUNKS, top_k=3)
    assert results
    assert "salary" in results[0].source_text.lower()


def test_clause_number_retrieval():
    results = RetrievalService().retrieve_chunks("What does clause 2 say?", CHUNKS, top_k=3)
    assert results[0].clause_number == "2"


def test_page_reference_retrieval():
    results = RetrievalService().retrieve_chunks("What is on page 2?", CHUNKS, top_k=3)
    assert all(chunk.page_start == 2 or chunk.page_end == 2 for chunk in results)


def test_missing_information_retrieval():
    results = RetrievalService().retrieve_chunks("stock option vesting cliff unicorn", CHUNKS, top_k=3)
    assert results == []


def test_partial_information_notice_query():
    results = RetrievalService().retrieve_chunks("What is the notice period?", CHUNKS, top_k=3)
    assert results
    assert "notice" in results[0].source_text.lower()


def test_multiple_relevant_clauses():
    results = RetrievalService().retrieve_chunks("termination after employment restriction", CHUNKS, top_k=5)
    ids = {chunk.chunk_id for chunk in results}
    assert "1" in ids
    assert "4" in ids
