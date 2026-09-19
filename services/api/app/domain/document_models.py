from datetime import datetime, timezone
from typing import Literal

from pydantic import Field

from app.domain.schemas import ApiModel, DocumentStatus, PageExtractionStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StoredPage(ApiModel):
    page_number: int
    raw_text: str
    normalized_text: str
    extraction_method: str = "pymupdf_text"
    extraction_status: PageExtractionStatus
    warnings: list[str] = Field(default_factory=list)
    start_offset: int
    end_offset: int


class StoredClause(ApiModel):
    clause_id: str
    clause_number: str | None
    title: str | None = None
    page_start: int
    page_end: int
    source_text: str
    start_offset: int
    end_offset: int


class StoredChunk(ApiModel):
    chunk_id: str
    clause_id: str | None
    clause_number: str | None
    page_start: int
    page_end: int
    source_text: str
    normalized_text: str
    start_offset: int
    end_offset: int


class StoredDocument(ApiModel):
    document_id: str
    original_filename: str
    stored_filename: str = "source.pdf"
    content_type: Literal["application/pdf"] = "application/pdf"
    file_size_bytes: int
    status: DocumentStatus = "uploaded"
    page_count: int | None = None
    warnings: list[str] = Field(default_factory=list)
    error_message: str | None = None
    pages: list[StoredPage] = Field(default_factory=list)
    clauses: list[StoredClause] = Field(default_factory=list)
    chunks: list[StoredChunk] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

