from fastapi import APIRouter, Depends

from app.config import get_settings
from app.domain.schemas import QuestionRequest, QuestionResponse
from app.services.document_store import DocumentStore
from app.services.qa_pipeline import QAPipeline

router = APIRouter(prefix="/documents/{document_id}/questions", tags=["questions"])


def get_qa_pipeline() -> QAPipeline:
    settings = get_settings()
    document_store = DocumentStore(storage_root=settings.document_storage_dir)
    return QAPipeline(document_store=document_store)


@router.post("", response_model=QuestionResponse)
def ask_question(
    document_id: str,
    request: QuestionRequest,
    qa_pipeline: QAPipeline = Depends(get_qa_pipeline),
) -> QuestionResponse:
    return qa_pipeline.ask_question(document_id, request)
