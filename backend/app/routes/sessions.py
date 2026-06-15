import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.schemas import SessionResponse, MessageResponse
from app.services import session_service

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    session = session_service.create_session(db, user["user_id"])
    return session


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return session_service.get_user_sessions(db, user["user_id"])


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    session = session_service.get_session(db, session_id, user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session_service.get_session_messages(db, session_id)

    result = []
    for m in messages:
        result.append(MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=json.loads(m.sources) if m.sources else None,
            created_at=m.created_at,
        ))
    return result


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    deleted = session_service.delete_session(db, session_id, user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}
