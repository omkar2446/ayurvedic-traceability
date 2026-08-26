from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth import get_current_user, get_db, require_roles
from app.models import HerbBatch, User, ProcessingRecord
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/processing", tags=["processing"])

class ProcessBatchRequest(BaseModel):
    input_quantity: float
    output_quantity: float
    process_type: Optional[str] = None
    processing_details: Optional[str] = None
    facility_location: Optional[str] = None
    processing_location: Optional[str] = None
    processing_date: Optional[datetime] = None
    notes: Optional[str] = None

class ProcessingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_id: str
    processor_id: Optional[int] = None
    input_quantity: float
    output_quantity: float
    loss_quantity: float
    processing_details: Optional[str] = None
    processing_location: Optional[str] = None
    processing_date: datetime
    status: str
    created_at: datetime

@router.post("/batch/{batch_id}", response_model=ProcessingResponse)
def process_batch(
    batch_id: str,
    payload: ProcessBatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProcessingRecord:
    from sqlalchemy import func
    batch_id_clean = batch_id.strip()
    batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == batch_id_clean.lower()).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")
        
    # Auto-claim custody during processing stage
    batch.current_holder_id = user.id
    if batch.recall_status and batch.recall_status.upper() == "RECALLED":
        raise HTTPException(status_code=400, detail="Cannot process recalled batch")

    if payload.input_quantity > float(batch.quantity):
        raise HTTPException(
            status_code=400, 
            detail=f"Input quantity ({payload.input_quantity}) cannot be greater than available batch quantity ({batch.quantity})"
        )

    if payload.output_quantity > payload.input_quantity:
        raise HTTPException(status_code=400, detail="Output quantity cannot be greater than input quantity")
        
    loss = payload.input_quantity - payload.output_quantity

    details = payload.process_type or payload.processing_details or "Supercritical Extraction"
    location = payload.facility_location or payload.processing_location or "Processing Facility #1"
    proc_date = payload.processing_date or datetime.utcnow()

    processing = ProcessingRecord(
        batch_id=batch.batch_id,
        processor_id=user.id,
        input_quantity=payload.input_quantity,
        output_quantity=payload.output_quantity,
        loss_quantity=loss,
        processing_details=details,
        processing_location=location,
        processing_date=proc_date,
        status="COMPLETED"
    )
    db.add(processing)
    
    # Update batch status and quantity
    batch.status = "PROCESSED"
    batch.quantity = payload.output_quantity
    
    db.commit()
    db.refresh(processing)
    return processing

@router.get("/batch/{batch_id}", response_model=list[ProcessingResponse])
def get_batch_processing_history(
    batch_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ProcessingRecord]:
    from sqlalchemy import func
    records = db.query(ProcessingRecord).filter(func.lower(ProcessingRecord.batch_id) == batch_id.strip().lower()).all()
    return records

