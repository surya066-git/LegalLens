from app.domain.schemas import QuestionRequest, QuestionResponse
from app.services.document_store import DocumentStore
from app.services.retrieval import RetrievalService
from app.services.llm import LLMService
from app.services.citation_validation import CitationValidationService
from app.services.errors import raise_api_error

class QAPipeline:
    def __init__(self, document_store: DocumentStore):
        self.document_store = document_store
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.citation_validator = CitationValidationService()

    def _check_prompt_injection(self, question: str):
        question_lower = question.lower()
        forbidden_phrases = [
            "ignore previous instructions",
            "ignore instructions",
            "system prompt",
            "api key",
            "you are now",
            "forget your instructions",
            "disregard all previous",
            "bypassing previous rules",
            "do not follow the rules",
            "reveal your instructions",
            "output your prompt"
        ]
        for phrase in forbidden_phrases:
            if phrase in question_lower:
                raise_api_error(400, "prompt_injection_detected", "Question rejected due to potential prompt injection.")

    def ask_question(self, document_id: str, request: QuestionRequest) -> QuestionResponse:
        self._check_prompt_injection(request.question)
        
        try:
            document = self.document_store.load_metadata(document_id)
        except Exception:
            raise_api_error(404, "DOCUMENT_NOT_FOUND", "Document not found")
        
        if not document.chunks:
            return QuestionResponse(
                status="NO_CHUNKS",
                answer="Document has no extracted chunks. Process it first.",
                confidence="low",
                insufficient_information=True,
                citations=[],
                ambiguities=[],
                lawyer_questions=[],
                disclaimer="This is legal information, not legal advice. Consult a qualified lawyer."
            )

        # 1. Retrieve relevant chunks
        relevant_chunks = self.retrieval_service.retrieve_chunks(request.question, document.chunks, top_k=15)
        
        if not relevant_chunks:
            return QuestionResponse(
                status="RETRIEVAL_EMPTY",
                answer="No supporting evidence was retrieved from the uploaded document.",
                confidence="low",
                insufficient_information=True,
                citations=[],
                ambiguities=[],
                lawyer_questions=[],
                disclaimer="This is legal information, not legal advice. Consult a qualified lawyer."
            )

        # 2. Generate answer using LLM
        response = self.llm_service.generate_answer(request.question, relevant_chunks, request.model_selection)
        response.status = "LLM_SUCCESS"
        
        # 3. Validate citations
        response = self.citation_validator.validate_citations(response, document.chunks)
        
        if response.status != "CITATION_VALIDATION_FAILED":
            response.status = "ANSWERED"
            
        return response
