from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class HealthResponse(ApiModel):
    status: Literal["ok"]
    app_name: str
    environment: str


DocumentStatus = Literal["uploaded", "processing", "processed", "failed"]
PageExtractionStatus = Literal["extracted", "potentially_scanned", "empty", "failed"]


class ErrorDetail(ApiModel):
    code: str
    message: str


class DocumentUploadResponse(ApiModel):
    document_id: str
    original_filename: str
    stored_filename: str
    status: Literal["uploaded"]
    file_size_bytes: int
    page_count: int
    message: str


class DocumentStatusResponse(ApiModel):
    document_id: str
    original_filename: str | None = None
    stored_filename: str | None = None
    status: DocumentStatus
    page_count: int | None = None
    file_size_bytes: int | None = None
    warnings: list[str] = Field(default_factory=list)
    error_message: str | None = None
    message: str


class ProcessDocumentResponse(ApiModel):
    document_id: str
    status: DocumentStatus
    page_count: int
    clause_count: int
    chunk_count: int
    warnings: list[str]
    message: str


class PageTextResponse(ApiModel):
    page_number: int
    raw_text: str
    normalized_text: str
    extraction_method: str
    extraction_status: PageExtractionStatus
    warnings: list[str]


class PagesResponse(ApiModel):
    document_id: str
    pages: list[PageTextResponse]


class ClauseResponse(ApiModel):
    clause_id: str
    clause_number: str | None
    display_clause_number: str
    title: str | None
    page_start: int
    page_end: int
    source_text: str
    start_offset: int
    end_offset: int


class ClausesResponse(ApiModel):
    document_id: str
    clauses: list[ClauseResponse]


class ChunkResponse(ApiModel):
    chunk_id: str
    clause_id: str | None
    clause_number: str | None
    page_start: int
    page_end: int
    source_text: str
    normalized_text: str
    start_offset: int
    end_offset: int


class ChunksResponse(ApiModel):
    document_id: str
    chunks: list[ChunkResponse]


class QuestionRequest(ApiModel):
    question: str = Field(min_length=1, examples=["Can my employer stop me from joining a competitor?"])


class Citation(ApiModel):
    page: int | None
    clause_number: str | None
    source_text: str
    chunk_id: str | None = None


class QuestionResponse(ApiModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    insufficient_information: bool
    citations: list[Citation]
    ambiguities: list[str]
    lawyer_questions: list[str]
    disclaimer: str
