from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import IdentityVerification, User


def test_registration_creates_pending_verification() -> None:
    suffix = uuid4().hex[:8]
    payload = {
        "full_name": "Traceability Applicant",
        "email": f"applicant-{suffix}@example.com",
        "username": f"applicant-{suffix}",
        "password": "StrongPass123!",
        "role": "COLLECTOR",
        "verification_document_type": "SOURCE_VERIFICATION",
        "verification_details": {"reference": "dev-reference"},
    }

    response = TestClient(app).post("/api/auth/register", json=payload)

    assert response.status_code == 201
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload["email"]).one()
        verification = db.query(IdentityVerification).filter(IdentityVerification.user_id == user.id).one()
        assert user.is_approved is False
        assert verification.verification_status == "PENDING"
        assert verification.verification_details == {"reference": "dev-reference"}
    finally:
        db.delete(verification)
        db.delete(user)
        db.commit()
        db.close()
