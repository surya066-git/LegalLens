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
        # Basic prompt injection checks as a secondary defense layer
        # The primary defense is evidence isolation in LLMService.
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
        
        # Load document metadata to ensure it exists and to get its chunks
        document = self.document_store.load_metadata(document_id)
        
        if not document.chunks:
            # If the document has no chunks yet, we can't answer.
            raise_api_error(400, "document_not_processed", "Document has no extracted chunks. Process it first.")

        # 1. Retrieve relevant chunks
        relevant_chunks = self.retrieval_service.retrieve_chunks(request.question, document.chunks, top_k=15)
        
        if not relevant_chunks:
            return QuestionResponse(
                answer="I cannot find any relevant information in the document for your question.",
                confidence="low",
                insufficient_information=True,
                citations=[],
                ambiguities=[],
                lawyer_questions=[],
                disclaimer="This is legal information, not legal advice. Consult a qualified lawyer."
            )

        # 2. Generate answer using LLM
        response = self.llm_service.generate_answer(request.question, relevant_chunks)
        
        # 3. Validate citations
        response = self.citation_validator.validate_citations(response, document.chunks)
        
        return response
