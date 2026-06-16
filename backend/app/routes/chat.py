import time
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_pipeline import answer_question
from app.services.embedder import embed_text
from app.services.vector_store import search
from app.services.generator import stream_answer
from app.services import session_service, analytics_service

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

    start_time = time.perf_counter()

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

    duration_ms = int((time.perf_counter() - start_time) * 1000)

    session_service.add_message(
        db, session_id, role="assistant", content=result["answer"], sources=result["sources"]
    )

    analytics_service.log_event(
        db, user["user_id"], event_type="chat", duration_ms=duration_ms
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=session_id,
    )


@router.post("/chat/stream")
async def chat_stream(
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

    query_embedding = embed_text(request.question, task_type="RETRIEVAL_QUERY")
    chunks = search(query_embedding, user_id=user["user_id"], top_k=request.top_k or 4, document_ids=request.document_ids)

    start_time = time.perf_counter()

    async def event_stream():
        full_answer = ""

        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        yield f"data: {json.dumps({'type': 'sources', 'sources': chunks})}\n\n"

        try:
            async for token in stream_answer(request.question, chunks):
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        session_service.add_message(
            db, session_id, role="assistant", content=full_answer, sources=chunks
        )

        analytics_service.log_event(
            db, user["user_id"], event_type="chat", duration_ms=duration_ms
        )

        yield f"data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
