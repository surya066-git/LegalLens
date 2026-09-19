import re
from pathlib import PurePath

import pymupdf
from fastapi import UploadFile

from app.config import Settings
from app.domain.document_models import StoredDocument
from app.services.document_store import DocumentStore
from app.services.errors import raise_api_error


PDF_EXTENSION = ".pdf"
SAFE_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,180}\.pdf$", re.IGNORECASE)


def validate_original_filename(filename: str | None) -> str:
    if filename is None or filename.strip() == "":
        raise_api_error(400, "missing_filename", "A PDF filename is required.")

    cleaned = filename.strip()
    if PurePath(cleaned).name != cleaned or "/" in cleaned or "\\" in cleaned or ".." in cleaned:
        raise_api_error(400, "unsafe_filename", "Unsafe filenames and path traversal attempts are not allowed.")

    if not cleaned.lower().endswith(PDF_EXTENSION):
        raise_api_error(400, "invalid_file_extension", "Only .pdf files are supported.")

    if SAFE_FILENAME_PATTERN.fullmatch(cleaned) is None:
        raise_api_error(400, "invalid_filename", "Filename contains unsupported characters.")

    return cleaned


async def read_and_validate_upload(file: UploadFile, settings: Settings) -> tuple[str, bytes, int]:
    original_filename = validate_original_filename(file.filename)

    if file.content_type != "application/pdf":
        raise_api_error(400, "invalid_content_type", "Upload must use content type application/pdf.")

    data = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break

        data.extend(chunk)
        if len(data) > settings.max_pdf_upload_bytes:
            raise_api_error(
                413,
                "file_too_large",
                f"PDF exceeds the configured size limit of {settings.max_pdf_upload_bytes} bytes.",
            )

    if not data:
        raise_api_error(400, "empty_file", "Uploaded PDF is empty.")

    page_count = validate_pdf_bytes(bytes(data))
    return original_filename, bytes(data), page_count


def validate_pdf_bytes(data: bytes) -> int:
    try:
        document = pymupdf.open(stream=data, filetype="pdf")
    except Exception:
        raise_api_error(400, "malformed_pdf", "Uploaded file is not a readable PDF.")

    try:
        if document.needs_pass:
            raise_api_error(400, "encrypted_pdf", "Password-protected PDFs are not supported yet.")

        if document.page_count <= 0:
            raise_api_error(400, "empty_pdf", "PDF does not contain any pages.")

        return document.page_count
    finally:
        document.close()


async def save_uploaded_pdf(file: UploadFile, settings: Settings) -> StoredDocument:
    original_filename, data, page_count = await read_and_validate_upload(file, settings)
    store = DocumentStore(settings.document_storage_dir)
    document_id = store.new_document_id()
    document_dir = store.create_document_dir(document_id)
    pdf_path = document_dir / "source.pdf"
    pdf_path.write_bytes(data)

    document = StoredDocument(
        document_id=document_id,
        original_filename=original_filename,
        file_size_bytes=len(data),
        page_count=page_count,
        status="uploaded",
        warnings=[],
    )
    store.save_metadata(document)
    return document
