import json
from sqlalchemy.orm import Session as DBSession
from app.models.db_models import ChatSession, Message


def create_session(db: DBSession, user_id: str) -> ChatSession:
    """Creates a new, empty chat session for a user."""
    session = ChatSession(user_id=user_id, title="New Chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_user_sessions(db: DBSession, user_id: str) -> list[ChatSession]:
    """Returns all sessions for a user, most recently updated first."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def get_session(db: DBSession, session_id: str, user_id: str) -> ChatSession | None:
    """Fetches one session, ensuring it belongs to the requesting user."""
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def get_session_messages(db: DBSession, session_id: str) -> list[Message]:
    """Returns all messages for a session, oldest first."""
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def add_message(
    db: DBSession,
    session_id: str,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> Message:
    """Saves a message to a session, and updates the session's title/timestamp."""
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        sources=json.dumps(sources) if sources else None,
    )
    db.add(message)

    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session and session.title == "New Chat" and role == "user":
        session.title = content[:60]

    db.commit()
    db.refresh(message)
    return message


def delete_session(db: DBSession, session_id: str, user_id: str) -> bool:
    """Deletes a session (and its messages, via cascade) if it belongs to the user."""
    session = get_session(db, session_id, user_id)
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True
