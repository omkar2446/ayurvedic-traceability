from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_db, require_roles
from app.models import HerbBatch, User
from app.schemas import BatchCreateRequest, BatchResponse

router = APIRouter(prefix="/api/batches", tags=["batches"])


def _batch_prefix(herb_name: str) -> str:
    letters = "".join(character for character in herb_name.upper() if character.isalpha())
    return (letters[:4] or "HERB").ljust(4, "X")


def _next_batch_id(db: Session, herb_name: str, year: int) -> str:
    prefix = _batch_prefix(herb_name)
    existing = db.query(HerbBatch.batch_id).filter(HerbBatch.batch_id.like(f"{prefix}-{year}-%")).all()
    sequence = len(existing) + 1
    candidate = f"{prefix}-{year}-{sequence:06d}"
    while db.query(HerbBatch.id).filter(HerbBatch.batch_id == candidate).first() is not None:
        sequence += 1
        candidate = f"{prefix}-{year}-{sequence:06d}"
    return candidate


@router.post("", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    payload: BatchCreateRequest,
    db: Session = Depends(get_db),
    collector: User = Depends(require_roles("ADMIN", "COLLECTOR")),
) -> HerbBatch:
    batch_id = _next_batch_id(db, payload.herb_name, payload.collection_date.year)
    batch = HerbBatch(
        batch_id=batch_id,
        herb_name=payload.herb_name,
        scientific_name=payload.scientific_name,
        quantity=payload.quantity,
        unit=payload.unit,
        collection_date=payload.collection_date,
        collection_location=payload.collection_location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        collector_id=collector.id,
        initial_holder_id=collector.id,
        current_holder_id=collector.id,
        source_type=payload.source_type,
        notes=payload.notes,
        status="CREATED",
        recall_status="ACTIVE",
    )
    db.add(batch)
    try:
        db.commit()
        db.refresh(batch)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Batch ID already exists") from exc
    return batch


@router.get("", response_model=list[BatchResponse])
def list_batches(
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[HerbBatch]:
    query = db.query(HerbBatch)
    if user.role == "COLLECTOR":
        query = query.filter(HerbBatch.collector_id == user.id)
    if search:
        pattern = f"%{search}%"
        query = query.filter((HerbBatch.batch_id.ilike(pattern)) | (HerbBatch.herb_name.ilike(pattern)))
    return query.order_by(HerbBatch.created_at.desc()).all()


@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)) -> HerbBatch:
    from sqlalchemy import func
    batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == batch_id.strip().lower()).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch