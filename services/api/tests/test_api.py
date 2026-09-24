from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from tests.helpers import employment_pdf, upload_file_tuple


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["storageMode"] == "ephemeral_local"


def test_invalid_json(client):
    uploaded = client.post("/documents", files=upload_file_tuple("agreement.pdf", employment_pdf()))
    doc_id = uploaded.json()["documentId"]
    response = client.post(
        f"/documents/{doc_id}/questions",
        content="{not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_missing_fields(client):
    uploaded = client.post("/documents", files=upload_file_tuple("agreement.pdf", employment_pdf()))
    doc_id = uploaded.json()["documentId"]
    response = client.post(f"/documents/{doc_id}/questions", json={})
    assert response.status_code == 422


def test_wrong_http_method(client):
    response = client.put("/health")
    assert response.status_code == 405
    response = client.get("/documents")
    assert response.status_code == 405


def test_large_question(client):
    uploaded = client.post("/documents", files=upload_file_tuple("agreement.pdf", employment_pdf()))
    doc_id = uploaded.json()["documentId"]
    response = client.post(
        f"/documents/{doc_id}/questions",
        json={"question": "A" * 5000},
    )
    assert response.status_code == 422


def test_concurrent_uploads(client):
    payload = employment_pdf()

    def upload() -> int:
        return client.post("/documents", files=upload_file_tuple("agreement.pdf", payload)).status_code

    with ThreadPoolExecutor(max_workers=4) as pool:
        codes = list(pool.map(lambda _: upload(), range(4)))
    assert all(code == 200 for code in codes)


def test_error_payload_has_no_stack_trace(client):
    response = client.get("/documents/doc_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assert response.status_code == 404
    assert "Traceback" not in response.text
    assert "File " not in response.text
