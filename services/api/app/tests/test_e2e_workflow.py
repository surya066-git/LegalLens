import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.domain.schemas import QuestionResponse, Citation


def test_e2e_smoke_workflow(client: TestClient, sample_pdf_bytes: bytes, settings):
    # 1. Upload
    upload_res = client.post(
        "/documents",
        files={"file": ("smoke_test.pdf", sample_pdf_bytes, "application/pdf")}
    )
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["documentId"]

    # 2. Process - Mock pymupdf.open to avoid needing a real complex PDF
    mock_pdf = MagicMock()
    mock_pdf.page_count = 1
    mock_page = MagicMock()
    mock_page.get_text.return_value = "1. Smoke Clause\nThis is a smoke test."
    mock_pdf.load_page.return_value = mock_page

    with patch("pymupdf.open", return_value=mock_pdf):
        process_res = client.post(f"/documents/{doc_id}/process")
        assert process_res.status_code == 200

    # 3. Verify status
    status_res = client.get(f"/documents/{doc_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "processed"
    assert status_res.json()["pageCount"] == 1

    # 4. Ask a supported question - Mock LLM to avoid real API call
    mock_llm_response = QuestionResponse(
        answer="This is a smoke test.",
        confidence="high",
        insufficient_information=False,
        citations=[Citation(page=1, clause_number="1.", source_text="This is a smoke test.")],
        ambiguities=[],
        lawyer_questions=[],
        disclaimer="Disclaimer"
    )
    
    with patch("app.services.qa_pipeline.LLMService.generate_answer", return_value=mock_llm_response):
        q_res = client.post(
            f"/documents/{doc_id}/questions",
            json={"question": "What kind of test is this?"}
        )
        assert q_res.status_code == 200
        data = q_res.json()
        assert data["insufficientInformation"] is False
        assert data["answer"] == "This is a smoke test."
        # Citation passes validation because the text exists in the mocked chunk
        assert len(data["citations"]) == 1

    # 5. Ask an unsupported question
    mock_llm_unsupported = QuestionResponse(
        answer="I don't know.",
        confidence="low",
        insufficient_information=True,
        citations=[],
        ambiguities=[],
        lawyer_questions=[],
        disclaimer="Disclaimer"
    )
    
    with patch("app.services.qa_pipeline.LLMService.generate_answer", return_value=mock_llm_unsupported):
        q_res_un = client.post(
            f"/documents/{doc_id}/questions",
            json={"question": "What is the meaning of life?"}
        )
        assert q_res_un.status_code == 200
        assert q_res_un.json()["insufficientInformation"] is True

    # 6. Delete document
    del_res = client.delete(f"/documents/{doc_id}")
    assert del_res.status_code == 200
    
    # Verify deletion
    status_res_after_del = client.get(f"/documents/{doc_id}")
    assert status_res_after_del.status_code == 404
