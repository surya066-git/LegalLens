from __future__ import annotations

import re

from app.config import get_settings
from app.domain.schemas import QuestionRequest, QuestionResponse
from app.services.citation_validation import CitationValidationService
from app.services.document_store import DocumentStore
from app.services.errors import raise_api_error
from app.services.llm import LLMService
from app.services.retrieval import RetrievalService

INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.I),
    re.compile(r"forget\s+(your|all)\s+(instructions|rules|prompt)", re.I),
    re.compile(r"reveal\s+(the\s+|your\s+)?(system\s+)?prompt", re.I),
    re.compile(r"(output|print|show)\s+(your|the)\s+(system\s+)?(prompt|instructions)", re.I),
    re.compile(r"disregard\s+(all\s+)?previous", re.I),
    re.compile(r"you\s+are\s+now\s+", re.I),
)

LEGAL_DISCLAIMER = "This is legal information, not legal advice. Consult a qualified lawyer."


class QAPipeline:
    def __init__(
        self,
        document_store: DocumentStore,
        llm_service: LLMService | None = None,
        retrieval_service: RetrievalService | None = None,
        citation_validator: CitationValidationService | None = None,
    ) -> None:
        self.document_store = document_store
        self._llm_service = llm_service
        self.retrieval_service = retrieval_service or RetrievalService()
        self.citation_validator = citation_validator or CitationValidationService()

    @property
    def llm_service(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service

    def _check_prompt_injection(self, question: str) -> None:
        for pattern in INJECTION_PATTERNS:
            if pattern.search(question):
                raise_api_error(
                    400,
                    "prompt_injection_detected",
                    "Question rejected due to potential prompt injection.",
                )

    def _empty_not_found(self, answer: str, status: str) -> QuestionResponse:
        return QuestionResponse(
            status=status,
            answer_type="NOT_FOUND",
            answer=answer,
            confidence="low",
            missing_information=[],
            citations=[],
            ambiguities=[],
            lawyer_questions=[],
            disclaimer=LEGAL_DISCLAIMER,
        )

    def ask_question(self, document_id: str, request: QuestionRequest) -> QuestionResponse:
        self._check_prompt_injection(request.question)

        try:
            document = self.document_store.load_metadata(document_id)
        except Exception:
            raise_api_error(404, "document_not_found", "Document was not found.")

        if document.status != "processed" or not document.chunks:
            return self._empty_not_found(
                "Document has no extracted text yet. Upload a readable PDF and wait until processing finishes.",
                "NO_CHUNKS",
            )

        settings = get_settings()
        relevant_chunks = self.retrieval_service.retrieve_chunks(
            request.question,
            document.chunks,
            top_k=settings.retrieval_top_k,
        )

        if not relevant_chunks:
            return self._empty_not_found(
                "No supporting evidence was retrieved from the uploaded document.",
                "RETRIEVAL_EMPTY",
            )

        response = self.llm_service.generate_answer(
            request.question,
            relevant_chunks,
            request.model_selection,
        )
        response.status = "LLM_SUCCESS"
        response = self.citation_validator.validate_citations(response, document.chunks)
        if response.status != "CITATION_VALIDATION_FAILED":
            response.status = "ANSWERED"
        return response
