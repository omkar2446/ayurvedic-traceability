from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import SessionLocal
from app.main import app
from app.models import User


def test_collector_can_create_batch_and_other_role_cannot() -> None:
    suffix = uuid4().hex[:8]
    db = SessionLocal()
    collector = User(
        email=f"collector-{suffix}@example.com",
        username=f"collector-{suffix}",
        password_hash=hash_password("StrongPass123!"),
        full_name="Test Collector",
        role="COLLECTOR",
        is_active=True,
        is_approved=True,
    )
    trader = User(
        email=f"trader-{suffix}@example.com",
        username=f"trader-{suffix}",
        password_hash=hash_password("StrongPass123!"),
        full_name="Test Trader",
        role="TRADER",
        is_active=True,
        is_approved=True,
    )
    db.add_all([collector, trader])
    db.commit()
    db.refresh(collector)
    db.refresh(trader)
    db.close()

    with TestClient(app) as client:
        collector_login = client.post("/api/auth/login", json={"email": collector.email, "password": "StrongPass123!"})
        trader_login = client.post("/api/auth/login", json={"email": trader.email, "password": "StrongPass123!"})
        payload = {
            "herb_name": "Ashwagandha",
            "scientific_name": "Withania somnifera",
            "quantity": 100,
            "unit": "kg",
            "collection_date": "2026-08-26T10:00:00",
            "collection_location": "Punjab",
            "latitude": 30.7333,
            "longitude": 76.7794,
            "notes": "Development test batch",
        }
        created = client.post(
            "/api/batches",
            json=payload,
            headers={"Authorization": f"Bearer {collector_login.json()['access_token']}"},
        )
        forbidden = client.post(
            "/api/batches",
            json=payload,
            headers={"Authorization": f"Bearer {trader_login.json()['access_token']}"},
        )

    assert created.status_code == 201
    assert created.json()["batch_id"].startswith("ASHW-2026-")
    assert created.json()["collector_id"] == collector.id
    assert forbidden.status_code == 403
