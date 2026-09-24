import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_pdf(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 21\n>>\nstream\nBT\n/F1 12 Tf\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000213 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n283\n%%EOF"
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(pdf_content)
    
    with open(pdf_file, "rb") as f:
        response = client.post("/documents", files={"file": ("test.pdf", f, "application/pdf")})
        
    assert response.status_code == 200
    data = response.json()
    assert "documentId" in data
    assert data["originalFilename"] == "test.pdf"
    
def test_upload_invalid_file(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("This is not a pdf.")
    
    with open(invalid_file, "rb") as f:
        response = client.post("/documents", files={"file": ("test.txt", f, "text/plain")})
        
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_file_extension"

def test_get_nonexistent_document(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    response = client.get("/documents/doc_12345678901234567890123456789012")
    assert response.status_code == 404

def test_upload_invalid_pdf_content(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"This is not a real PDF file.")
    
    with open(pdf_file, "rb") as f:
        response = client.post("/documents", files={"file": ("test.pdf", f, "application/pdf")})
        
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "malformed_pdf"

def test_delete_document(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_DIR", str(tmp_path))
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 21\n>>\nstream\nBT\n/F1 12 Tf\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000213 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n283\n%%EOF"
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(pdf_content)
    
    with open(pdf_file, "rb") as f:
        response = client.post("/documents", files={"file": ("test.pdf", f, "application/pdf")})
    
    doc_id = response.json()["documentId"]
    
    del_response = client.delete(f"/documents/{doc_id}")
    assert del_response.status_code == 200
    
    get_response = client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 404
