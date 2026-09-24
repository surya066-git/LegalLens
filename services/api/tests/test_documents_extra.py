def test_get_pages(client):
    from tests.test_documents import _upload
    doc_id = _upload(client)
    client.post(f"/documents/{doc_id}/process")
    pages = client.get(f"/documents/{doc_id}/pages")
    assert pages.status_code == 200

def test_get_page_not_found(client):
    from tests.test_documents import _upload
    doc_id = _upload(client)
    client.post(f"/documents/{doc_id}/process")
    page = client.get(f"/documents/{doc_id}/pages/999")
    assert page.status_code == 404
