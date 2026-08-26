from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth import get_current_user, get_db, require_roles
from app.models import HerbBatch, User, LabReport
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import hashlib

router = APIRouter(prefix="/api/laboratory", tags=["laboratory"])

class LabTestRequest(BaseModel):
    certificate_id: str
    test_type: Optional[str] = None
    test_date: Optional[datetime] = None
    result: str = "PASSED" # PASSED, FAILED, PENDING
    report_url: Optional[str] = None
    notes: Optional[str] = None

class LabTestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    certificate_id: str
    batch_id: str
    report_hash: str
    result: str
    report_url: Optional[str] = None
    test_type: Optional[str] = None
    test_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime

@router.post("/batch/{batch_id}", response_model=LabTestResponse)
def add_lab_test(
    batch_id: str,
    payload: LabTestRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("ADMIN", "LABORATORY")),
) -> LabReport:
    from sqlalchemy import func
    batch_id_clean = batch_id.strip()
    batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == batch_id_clean.lower()).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    ttype = payload.test_type or "Purity & Heavy Metals Assay"
    tdate = payload.test_date or datetime.utcnow()

    # Generate simple hash for off-chain doc
    report_content_placeholder = f"{payload.certificate_id}-{payload.result}-{tdate}"
    report_hash = hashlib.sha256(report_content_placeholder.encode()).hexdigest()

    lab_report = LabReport(
        certificate_id=payload.certificate_id,
        batch_id=batch.batch_id,
        laboratory_id=user.id,
        report_hash=report_hash,
        result=payload.result,
        report_url=payload.report_url,
        test_type=ttype,
        test_date=tdate,
        notes=payload.notes
    )
    db.add(lab_report)
    
    batch.status = "TESTED"
    
    db.commit()
    db.refresh(lab_report)
    return lab_report

@router.get("/batch/{batch_id}", response_model=list[LabTestResponse])
def get_batch_lab_tests(
    batch_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[LabReport]:
    from sqlalchemy import func
    reports = db.query(LabReport).filter(func.lower(LabReport.batch_id) == batch_id.strip().lower()).all()
    return reports
