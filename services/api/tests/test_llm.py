import pytest
from unittest.mock import patch, MagicMock
from app.services.llm import LLMService, build_evidence_prompt, _extract_json_object, QuestionResponse
from app.domain.document_models import StoredChunk
from fastapi import HTTPException
from pydantic import SecretStr

@pytest.fixture
def sample_chunks():
    return [
        StoredChunk(chunk_id="c1", document_id="d1", source_text="Chunk 1", page_start=1, page_end=1, clause_number="1.1", token_count=10, clause_id="c1", normalized_text="chunk 1", start_offset=0, end_offset=10),
        StoredChunk(chunk_id="c2", document_id="d1", source_text="Chunk 2", page_start=2, page_end=2, clause_number="1.2", token_count=10, clause_id="c2", normalized_text="chunk 2", start_offset=0, end_offset=10)
    ]

def test_build_evidence_prompt(sample_chunks):
    prompt = build_evidence_prompt("What is it?", sample_chunks)
    assert "User Question:" in prompt
    assert "What is it?" in prompt
    assert "chunk_id=c1 page=1 clause=1.1" in prompt
    assert "Chunk 1" in prompt

def test_extract_json_object():
    assert _extract_json_object('{"a": 1}') == '{"a": 1}'
    assert _extract_json_object('some text {"a": 1} other text') == '{"a": 1}'
    with pytest.raises(ValueError):
        _extract_json_object('no json here')

@patch('app.services.llm.genai.Client')
def test_llm_service_gemini_success(mock_client_class, sample_chunks):
    service = LLMService()
    mock_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"status": "ANSWERED", "answer_type": "DIRECTLY_ANSWERED", "answer": "Test", "confidence": "high", "missing_information": [], "citations": [], "ambiguities": [], "lawyer_questions": [], "disclaimer": "test"}'
    mock_instance.models.generate_content.return_value = mock_response
    service.clients = [mock_instance]
    
    resp = service.generate_answer("Test question", sample_chunks)
    assert resp.answer == "Test"
    assert resp.answer_type == "DIRECTLY_ANSWERED"

@patch('app.services.llm.httpx.Client.post')
def test_llm_service_groq_success(mock_post, sample_chunks):
    service = LLMService()
    service.clients = []
    service._groq_key = SecretStr("test_key")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {"message": {"content": '{"status": "ANSWERED", "answer_type": "DIRECTLY_ANSWERED", "answer": "Groq Test", "confidence": "high", "missing_information": [], "citations": [], "ambiguities": [], "lawyer_questions": [], "disclaimer": "test"}'}}
        ]
    }
    mock_post.return_value = mock_resp
    
    resp = service.generate_answer("Test question", sample_chunks, model_selection="grok")
    assert resp.answer == "Groq Test"

@patch('app.services.llm.httpx.Client.post')
def test_llm_service_groq_error(mock_post, sample_chunks):
    service = LLMService()
    service.clients = []
    service._groq_key = SecretStr("test_key")
    
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_post.return_value = mock_resp
    
    with pytest.raises(HTTPException):
        service.generate_answer("Test question", sample_chunks, model_selection="grok")
