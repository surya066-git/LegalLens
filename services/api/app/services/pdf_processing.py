import pymupdf

from app.config import Settings
from app.domain.document_models import StoredDocument, StoredPage
from app.services.chunking import chunk_document
from app.services.clause_detection import detect_clauses
from app.services.document_store import DocumentStore
from app.services.errors import raise_api_error
from app.services.text_normalization import normalize_search_text


def process_pdf_document(document_id: str, settings: Settings) -> StoredDocument:
    store = DocumentStore(settings.document_storage_dir)
    document = store.load_metadata(document_id)
    pdf_path = store.pdf_path(document_id)

    if not pdf_path.exists():
        raise_api_error(404, "pdf_not_found", "Stored PDF file was not found.")

    try:
        document.status = "processing"
        store.save_metadata(document)

        pages = extract_pages(pdf_path, settings)
        clauses = detect_clauses(pages)
        chunks = chunk_document(pages, clauses)

        document.pages = pages
        document.clauses = clauses
        document.chunks = chunks
        document.page_count = len(pages)
        document.status = "processed"
        document.error_message = None
        document.warnings = sorted({warning for page in pages for warning in page.warnings})
        store.save_metadata(document)
        return document
    except Exception as error:
        document.status = "failed"
        document.error_message = str(error)
        store.save_metadata(document)
        raise


def extract_pages(pdf_path, settings: Settings) -> list[StoredPage]:
    try:
        pdf = pymupdf.open(pdf_path)
    except Exception:
        raise_api_error(400, "malformed_pdf", "Stored PDF could not be opened for processing.")

    pages: list[StoredPage] = []
    offset = 0
    try:
        for index in range(pdf.page_count):
            page_number = index + 1
            warnings: list[str] = []
            try:
                raw_text = pdf.load_page(index).get_text("text")
                extraction_status = "extracted"
                if not raw_text.strip():
                    extraction_status = "empty"
                    warnings.append("No extractable text found on this page. OCR is not yet supported.")
                elif len(raw_text.strip()) < settings.min_extractable_text_chars:
                    extraction_status = "potentially_scanned"
                    warnings.append("Little extractable text found on this page. OCR is not yet supported.")
            except Exception as error:
                raw_text = ""
                extraction_status = "failed"
                warnings.append(f"Text extraction failed for this page: {error}")

            page_start = offset
            page_end = page_start + len(raw_text)
            pages.append(
                StoredPage(
                    page_number=page_number,
                    raw_text=raw_text,
                    normalized_text=normalize_search_text(raw_text),
                    extraction_method="pymupdf_text",
                    extraction_status=extraction_status,
                    warnings=warnings,
                    start_offset=page_start,
                    end_offset=page_end,
                )
            )
            offset = page_end + 2
    finally:
        pdf.close()

    return pages
