from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_db, require_roles
from app.models import IdentityVerification, User
from app.schemas import VerificationResponse

router = APIRouter(prefix="/api/admin/verifications", tags=["admin"])


@router.get("", response_model=list[VerificationResponse])
def list_verifications(db: Session = Depends(get_db), _admin: User = Depends(require_roles("ADMIN"))):
    return db.query(IdentityVerification).order_by(IdentityVerification.submitted_at.desc()).all()


@router.post("/{verification_id}/approve", response_model=VerificationResponse)
def approve_verification(verification_id: int, db: Session = Depends(get_db), admin: User = Depends(require_roles("ADMIN"))):
    verification = db.get(IdentityVerification, verification_id)
    if verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
    verification.verification_status = "VERIFIED"
    verification.reviewed_at = datetime.utcnow()
    verification.reviewed_by = admin.id
    user = db.get(User, verification.user_id)
    user.is_approved = True
    db.commit()
    db.refresh(verification)
    return verification


@router.post("/{verification_id}/reject", response_model=VerificationResponse)
def reject_verification(verification_id: int, reason: str = "Verification rejected", db: Session = Depends(get_db), admin: User = Depends(require_roles("ADMIN"))):
    verification = db.get(IdentityVerification, verification_id)
    if verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
    verification.verification_status = "REJECTED"
    verification.rejection_reason = reason
    verification.reviewed_at = datetime.utcnow()
    verification.reviewed_by = admin.id
    db.commit()
    db.refresh(verification)
    return verification