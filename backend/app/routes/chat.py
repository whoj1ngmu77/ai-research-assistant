from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import answer_question
from app.services import session_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if request.session_id:
        session = session_service.get_session(db, request.session_id, user["user_id"])
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = session.id
    else:
        session = session_service.create_session(db, user["user_id"])
        session_id = session.id

    session_service.add_message(db, session_id, role="user", content=request.question)

    try:
        result = answer_question(
            question=request.question,
            user_id=user["user_id"],
            document_ids=request.document_ids,
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to generate answer: {str(e)}"
        )

    session_service.add_message(
        db, session_id, role="assistant", content=result["answer"], sources=result["sources"]
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session_id,
    )
