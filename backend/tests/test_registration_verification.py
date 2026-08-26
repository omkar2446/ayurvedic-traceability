from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_registration_creates_pending_admin_verification() -> None:
    suffix = uuid4().hex[:8]
    payload = {
        "full_name": "Pending Collector",
        "email": f"collector-{suffix}@example.com",
        "username": f"collector-{suffix}",
        "password": "StrongPass123!",
        "role": "COLLECTOR",
        "verification_document_type": "SOURCE_VERIFICATION",
        "verification_details": {"reference": "ROLE-REF-001"},
    }

    with TestClient(app) as client:
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["is_approved"] is False

        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "ChangeMe123!"},
        )
        assert admin_login.status_code == 200
        token = admin_login.json()["access_token"]
        verification_response = client.get(
            "/api/admin/verifications",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert verification_response.status_code == 200
    records = verification_response.json()
    record = next(item for item in records if item["user_id"] == created_user["id"])
    assert record["verification_status"] == "PENDING"
    assert record["document_type"] == "SOURCE_VERIFICATION"
    assert record["verification_details"] == {"reference": "ROLE-REF-001"}
