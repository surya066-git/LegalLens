import pytest
from app.domain.document_models import StoredChunk
from app.services.retrieval import RetrievalService

def test_tokenize():
    from app.services.retrieval import tokenize
    tokens = tokenize("This is a simple test, with 123 numbers!")
    assert "simple" in tokens
    assert "test" in tokens
    assert "123" in tokens
    # stop words removed
    assert "this" not in tokens
    assert "is" not in tokens
    assert "a" not in tokens
    assert "with" not in tokens

def test_retrieve_chunks():
    chunks = [
        StoredChunk(
            chunk_id="c1",
            clause_id=None,
            clause_number=None,
            page_start=1,
            page_end=1,
            source_text="The employee shall have a notice period of 30 days.",
            normalized_text="the employee shall have a notice period of 30 days.",
            start_offset=0,
            end_offset=50
        ),
        StoredChunk(
            chunk_id="c2",
            clause_id=None,
            clause_number=None,
            page_start=2,
            page_end=2,
            source_text="The salary is 100,000 USD.",
            normalized_text="the salary is 100,000 usd.",
            start_offset=0,
            end_offset=30
        )
    ]
    
    service = RetrievalService()
    
    # query matching c1
    results = service.retrieve_chunks("What is the notice period?", chunks, top_k=5)
    assert len(results) > 0
    assert results[0].chunk_id == "c1"
    
    # query matching c2
    results2 = service.retrieve_chunks("What is the salary?", chunks, top_k=5)
    assert len(results2) > 0
    assert results2[0].chunk_id == "c2"

    results3 = service.retrieve_chunks("What is the weather?", chunks, top_k=5)
    assert len(results3) > 0  # Keyword search might still return random chunks if no exact match, but scored low
    
    # Test empty chunks
    results_empty = service.retrieve_chunks("Notice period", [], top_k=5)
    assert len(results_empty) == 0

def test_retrieval_limitations():
    # Documenting and testing keyword retrieval limitation
    # Stop words and common words shouldn't break the system but don't guarantee semantic matches
    chunks = [
        StoredChunk(
            chunk_id="c1",
            clause_id=None,
            clause_number=None,
            page_start=1,
            page_end=1,
            source_text="The company provides a laptop.",
            normalized_text="the company provides a laptop.",
            start_offset=0,
            end_offset=30
        )
    ]
    service = RetrievalService()
    
    # "is there a" are stop words, so this is an empty token query
    results = service.retrieve_chunks("Is there a", chunks, top_k=5)
    # Our retrieval logic might fallback or return all if tokens are empty
    # We just ensure it doesn't crash
    assert isinstance(results, list)
