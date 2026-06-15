from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answer_question(
            question=request.question,
            document_ids=request.document_ids,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to generate answer: {str(e)}"
        )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
    )
