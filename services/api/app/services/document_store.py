import json
import logging
import re
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

from app.domain.document_models import StoredDocument, utc_now
from app.services.errors import raise_api_error


DOCUMENT_ID_PATTERN = re.compile(r"^doc_[a-f0-9]{32}$")


class DocumentStore:
    def __init__(self, storage_root: Path) -> None:
        self.storage_root = storage_root.resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def new_document_id(self) -> str:
        return f"doc_{uuid.uuid4().hex}"

    def create_document_dir(self, document_id: str) -> Path:
        document_dir = self._document_dir(document_id)
        document_dir.mkdir(parents=False, exist_ok=False)
        return document_dir

    def pdf_path(self, document_id: str) -> Path:
        return self._document_dir(document_id) / "source.pdf"

    def save_metadata(self, document: StoredDocument) -> None:
        document.updated_at = utc_now()
        path = self.metadata_path(document.document_id)
        path.write_text(
            json.dumps(document.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )

    def load_metadata(self, document_id: str) -> StoredDocument:
        path = self.metadata_path(document_id)
        if not path.exists():
            raise_api_error(404, "document_not_found", "Document was not found.")
        return StoredDocument.model_validate_json(path.read_text(encoding="utf-8"))

    def list_document_ids(self) -> list[str]:
        ids: list[str] = []
        for path in self.storage_root.iterdir():
            if path.is_dir() and DOCUMENT_ID_PATTERN.fullmatch(path.name):
                ids.append(path.name)
        return sorted(ids)

    def delete_document(self, document_id: str) -> None:
        import shutil
        document_dir = self._document_dir(document_id)
        if not document_dir.exists():
            raise_api_error(404, "document_not_found", "Document was not found.")
        try:
            shutil.rmtree(document_dir)
        except OSError:
            logger.exception("Failed to delete %s", document_id)
            raise_api_error(500, "deletion_failed", "Failed to delete document files.")

    def metadata_path(self, document_id: str) -> Path:
        return self._document_dir(document_id) / "metadata.json"

    def _document_dir(self, document_id: str) -> Path:
        if not DOCUMENT_ID_PATTERN.fullmatch(document_id):
            raise_api_error(404, "document_not_found", "Document was not found.")

        document_dir = (self.storage_root / document_id).resolve()
        if not document_dir.is_relative_to(self.storage_root):
            raise_api_error(400, "unsafe_path", "Unsafe document path was rejected.")

        return document_dir

