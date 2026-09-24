from __future__ import annotations

import re

from app.domain.document_models import StoredChunk
from app.domain.schemas import QuestionResponse


def normalize_for_citation(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\W_]+", " ", text)
    return text.lower().strip()


class CitationValidationService:
    def validate_citations(self, response: QuestionResponse, chunks: list[StoredChunk]) -> QuestionResponse:
        valid_citations = []
        for citation in response.citations:
            norm_citation = normalize_for_citation(citation.source_text)
            if len(norm_citation) < 12:
                continue

            matched_chunk: StoredChunk | None = None
            for chunk in chunks:
                norm_chunk = normalize_for_citation(chunk.source_text)
                if not norm_chunk:
                    continue
                if norm_citation in norm_chunk or (
                    len(norm_chunk) >= 40 and norm_chunk in norm_citation
                ):
                    matched_chunk = chunk
                    break

            if matched_chunk is None:
                continue

            citation.chunk_id = matched_chunk.chunk_id
            citation.page = matched_chunk.page_start
            citation.clause_number = matched_chunk.clause_number
            valid_citations.append(citation)

        if response.citations and not valid_citations:
            response.status = "CITATION_VALIDATION_FAILED"
            response.answer_type = "NOT_FOUND"
            response.confidence = "low"
            response.citations = []
            response.answer = (
                "I cannot find sufficient evidence in the document to answer this question accurately."
            )
            response.missing_information = ["Verified source text for the generated answer"]
        else:
            response.citations = valid_citations

        return response
