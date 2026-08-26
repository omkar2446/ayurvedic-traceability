from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.auth import get_current_user, get_db, require_roles
from app.models import HerbBatch, User, CustodyTransfer
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/transfers", tags=["transfers"])

class TransferCreateRequest(BaseModel):
    to_user_id: int
    notes: Optional[str] = None

class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    batch_id: str
    from_user_id: Optional[int] = None
    to_user_id: Optional[int] = None
    quantity: float
    location: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

@router.post("/batch/{batch_id}", response_model=TransferResponse)
def initiate_transfer(
    batch_id: str,
    payload: TransferCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CustodyTransfer:
    from sqlalchemy import func
    batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == batch_id.strip().lower()).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")
        
    if user.role != "ADMIN" and batch.current_holder_id != user.id:
        # Auto-claim custody if unassigned or initiating transfer in supply chain
        batch.current_holder_id = user.id
    if batch.recall_status and batch.recall_status.upper() == "RECALLED":
        raise HTTPException(status_code=400, detail="Cannot transfer recalled batch")

    to_user = db.query(User).filter(User.id == payload.to_user_id).first()
    if not to_user:
        raise HTTPException(status_code=404, detail="Recipient user not found")

    transfer = CustodyTransfer(
        batch_id=batch.batch_id,
        from_user_id=user.id,
        to_user_id=to_user.id,
        quantity=batch.quantity,
        notes=payload.notes,
        status="PENDING",
    )
    db.add(transfer)
    
    # Update batch status
    batch.status = "IN_TRANSIT"
    
    db.commit()
    db.refresh(transfer)
    return transfer

@router.get("/incoming", response_model=list[TransferResponse])
def get_incoming_transfers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CustodyTransfer]:
    transfers = db.query(CustodyTransfer).filter(
        CustodyTransfer.to_user_id == user.id,
        CustodyTransfer.status == "PENDING"
    ).order_by(CustodyTransfer.created_at.desc()).all()
    return transfers

@router.post("/{transfer_id}/accept", response_model=TransferResponse)
def accept_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CustodyTransfer:
    transfer = db.query(CustodyTransfer).filter(CustodyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if transfer.to_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if transfer.status != "PENDING":
        raise HTTPException(status_code=400, detail="Transfer is not pending")

    batch = db.query(HerbBatch).filter(HerbBatch.batch_id == transfer.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    transfer.status = "ACCEPTED"
    transfer.updated_at = datetime.utcnow()
    
    batch.current_holder_id = user.id
    batch.status = "ACCEPTED"
    
    db.commit()
    db.refresh(transfer)
    return transfer

@router.post("/{transfer_id}/reject", response_model=TransferResponse)
def reject_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CustodyTransfer:
    transfer = db.query(CustodyTransfer).filter(CustodyTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    if transfer.to_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if transfer.status != "PENDING":
        raise HTTPException(status_code=400, detail="Transfer is not pending")

    batch = db.query(HerbBatch).filter(HerbBatch.batch_id == transfer.batch_id).first()
    
    transfer.status = "REJECTED"
    transfer.updated_at = datetime.utcnow()
    
    if batch:
        batch.status = "REJECTED_TRANSFER"
        
    db.commit()
    db.refresh(transfer)
    return transfer

@router.get("/history", response_model=list[TransferResponse])
def get_transfer_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CustodyTransfer]:
    transfers = db.query(CustodyTransfer).filter(
        or_(CustodyTransfer.from_user_id == user.id, CustodyTransfer.to_user_id == user.id)
    ).order_by(CustodyTransfer.created_at.desc()).all()
    return transfers
