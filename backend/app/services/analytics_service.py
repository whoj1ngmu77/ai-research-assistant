from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession
from app.models.db_models import UsageEvent


def log_event(
    db: DBSession,
    user_id: str,
    event_type: str,
    duration_ms: int | None = None,
    chunks_count: int | None = None,
) -> None:
    """Records a usage event. Does not raise on failure — analytics should never break core features."""
    try:
        event = UsageEvent(
            user_id=user_id,
            event_type=event_type,
            duration_ms=duration_ms,
            chunks_count=chunks_count,
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()


def get_user_stats(db: DBSession, user_id: str) -> dict:
    """Returns aggregate usage stats for a single user."""
    documents_uploaded = (
        db.query(func.count(UsageEvent.id))
        .filter(UsageEvent.user_id == user_id, UsageEvent.event_type == "upload")
        .scalar()
    ) or 0

    questions_asked = (
        db.query(func.count(UsageEvent.id))
        .filter(UsageEvent.user_id == user_id, UsageEvent.event_type == "chat")
        .scalar()
    ) or 0

    avg_response_time_ms = (
        db.query(func.avg(UsageEvent.duration_ms))
        .filter(
            UsageEvent.user_id == user_id,
            UsageEvent.event_type == "chat",
            UsageEvent.duration_ms.isnot(None),
        )
        .scalar()
    )

    total_chunks = (
        db.query(func.sum(UsageEvent.chunks_count))
        .filter(UsageEvent.user_id == user_id, UsageEvent.event_type == "upload")
        .scalar()
    ) or 0

    return {
        "documents_uploaded": documents_uploaded,
        "questions_asked": questions_asked,
        "avg_response_time_ms": round(avg_response_time_ms, 1) if avg_response_time_ms else None,
        "total_chunks_stored": total_chunks,
    }
