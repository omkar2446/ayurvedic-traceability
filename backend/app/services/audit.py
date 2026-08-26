from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit(db: Session, user_id: int | None, event_type: str, entity_type: str | None, entity_id: str | None, description: str, metadata: dict | None = None) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            event_metadata=metadata or {},
        )
    )
    db.commit()
