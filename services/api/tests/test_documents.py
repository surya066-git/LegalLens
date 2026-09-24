from __future__ import annotations

from app.services.document_store import DocumentStore
from tests.helpers import employment_pdf, upload_file_tuple


def _upload(client):
    response = client.post("/documents", files=upload_file_tuple("contract.pdf", employment_pdf()))
    assert response.status_code == 200
    return response.json()["documentId"]


def test_create_and_retrieve_document(client):
    doc_id = _upload(client)
    response = client.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["documentId"] == doc_id
    assert data["status"] == "uploaded"


def test_list_documents_in_store(client, storage_dir):
    first = _upload(client)
    second = _upload(client)
    store = DocumentStore(storage_dir)
    listed = store.list_document_ids()
    assert first in listed
    assert second in listed
    assert len(listed) == 2


def test_process_document(client):
    doc_id = _upload(client)
    response = client.post(f"/documents/{doc_id}/process")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["pageCount"] >= 1
    assert data["chunkCount"] >= 1
    assert data["clauseCount"] >= 1


def test_get_pages_clauses_chunks(client):
    doc_id = _upload(client)
    client.post(f"/documents/{doc_id}/process")
    pages = client.get(f"/documents/{doc_id}/pages")
    assert pages.status_code == 200
    assert pages.json()["pages"]
    clauses = client.get(f"/documents/{doc_id}/clauses")
    assert clauses.status_code == 200
    assert clauses.json()["clauses"]
    chunks = client.get(f"/documents/{doc_id}/chunks")
    assert chunks.status_code == 200
    assert chunks.json()["chunks"]


def test_delete_document(client):
    doc_id = _upload(client)
    deleted = client.delete(f"/documents/{doc_id}")
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"
    missing = client.get(f"/documents/{doc_id}")
    assert missing.status_code == 404


def test_delete_nonexistent_document(client):
    response = client.delete("/documents/doc_12345678901234567890123456789012")
    assert response.status_code == 404


def test_duplicate_delete(client):
    doc_id = _upload(client)
    assert client.delete(f"/documents/{doc_id}").status_code == 200
    assert client.delete(f"/documents/{doc_id}").status_code == 404


def test_invalid_document_id_rejected(client):
    response = client.get("/documents/../../etc/passwd")
    assert response.status_code in {404, 422}


def test_unprocessed_clauses_conflict(client):
    doc_id = _upload(client)
    response = client.get(f"/documents/{doc_id}/clauses")
    assert response.status_code == 409
