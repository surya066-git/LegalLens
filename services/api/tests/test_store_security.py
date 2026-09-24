import pytest
from fastapi import HTTPException

from app.services.document_store import DocumentStore


def test_document_id_rejects_path_escape(tmp_path):
    store = DocumentStore(tmp_path)
    with pytest.raises(HTTPException) as exc:
        store._document_dir("../outside")
    assert exc.value.status_code == 404
