from fastapi import APIRouter, Depends, File, UploadFile

from app.config import Settings, get_settings
from app.domain.document_models import StoredDocument
from app.domain.schemas import (
    ChunkResponse,
    ChunksResponse,
    ClauseResponse,
    ClausesResponse,
    DocumentDeleteResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
    PagesResponse,
    PageTextResponse,
    ProcessDocumentResponse,
)
from app.services.document_store import DocumentStore
from app.services.errors import raise_api_error
from app.services.pdf_processing import process_pdf_document
from app.services.pdf_uploads import save_uploaded_pdf


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> DocumentUploadResponse:
    document = await save_uploaded_pdf(file, settings)
    return DocumentUploadResponse(
        document_id=document.document_id,
        original_filename=document.original_filename,
        stored_filename=document.stored_filename,
        status="uploaded",
        file_size_bytes=document.file_size_bytes,
        page_count=document.page_count or 0,
        message="PDF uploaded and validated. Call the process endpoint to extract page-aware text.",
    )


@router.post("/{documentId}/process", response_model=ProcessDocumentResponse)
def process_document(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> ProcessDocumentResponse:
    document = process_pdf_document(documentId, settings)
    return ProcessDocumentResponse(
        document_id=document.document_id,
        status=document.status,
        page_count=document.page_count or 0,
        clause_count=len(document.clauses),
        chunk_count=len(document.chunks),
        warnings=document.warnings,
        message="PDF processed with page-aware PyMuPDF text extraction. OCR is not yet supported.",
    )


@router.get("/{documentId}", response_model=DocumentStatusResponse)
def get_document(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> DocumentStatusResponse:
    document = _load_document(documentId, settings)
    return DocumentStatusResponse(
        document_id=document.document_id,
        original_filename=document.original_filename,
        stored_filename=document.stored_filename,
        status=document.status,
        page_count=document.page_count,
        file_size_bytes=document.file_size_bytes,
        warnings=document.warnings,
        error_message=document.error_message,
        message=_status_message(document),
    )


@router.delete("/{documentId}", response_model=DocumentDeleteResponse)
def delete_document(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> DocumentDeleteResponse:
    # Document IDs are unguessable UUIDs. There is no account model; possession of the ID is the access token.
    store = DocumentStore(settings.document_storage_dir)
    store.delete_document(documentId)
    return DocumentDeleteResponse(
        status="deleted",
        document_id=documentId,
        message="Document successfully deleted.",
    )


@router.get("/{documentId}/clauses", response_model=ClausesResponse)
def get_clauses(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> ClausesResponse:
    document = _load_processed_document(documentId, settings)
    return ClausesResponse(
        document_id=document.document_id,
        clauses=[
            ClauseResponse(
                clause_id=clause.clause_id,
                clause_number=clause.clause_number,
                display_clause_number=clause.clause_number or "No clause number present",
                title=clause.title,
                page_start=clause.page_start,
                page_end=clause.page_end,
                source_text=clause.source_text,
                start_offset=clause.start_offset,
                end_offset=clause.end_offset,
            )
            for clause in document.clauses
        ],
    )


@router.get("/{documentId}/chunks", response_model=ChunksResponse)
def get_chunks(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> ChunksResponse:
    document = _load_processed_document(documentId, settings)
    return ChunksResponse(
        document_id=document.document_id,
        chunks=[ChunkResponse.model_validate(chunk) for chunk in document.chunks],
    )


@router.get("/{documentId}/pages", response_model=PagesResponse)
def get_pages(
    documentId: str,
    settings: Settings = Depends(get_settings),
) -> PagesResponse:
    document = _load_processed_document(documentId, settings)
    return PagesResponse(
        document_id=document.document_id,
        pages=[PageTextResponse.model_validate(page) for page in document.pages],
    )


@router.get("/{documentId}/pages/{pageNumber}", response_model=PageTextResponse)
def get_page(
    documentId: str,
    pageNumber: int,
    settings: Settings = Depends(get_settings),
) -> PageTextResponse:
    document = _load_processed_document(documentId, settings)
    for page in document.pages:
        if page.page_number == pageNumber:
            return PageTextResponse.model_validate(page)

    raise_api_error(404, "page_not_found", "Page was not found for this document.")


def _load_document(document_id: str, settings: Settings) -> StoredDocument:
    return DocumentStore(settings.document_storage_dir).load_metadata(document_id)


def _load_processed_document(document_id: str, settings: Settings) -> StoredDocument:
    document = _load_document(document_id, settings)
    if document.status != "processed":
        raise_api_error(409, "document_not_processed", "Document has not been processed yet.")
    return document


def _status_message(document: StoredDocument) -> str:
    if document.status == "uploaded":
        return "PDF uploaded and waiting for processing."
    if document.status == "processing":
        return "PDF processing is in progress."
    if document.status == "processed":
        return "PDF processed with page-aware text extraction."
    return "PDF processing failed."
