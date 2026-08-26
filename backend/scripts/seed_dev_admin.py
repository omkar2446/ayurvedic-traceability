"""Create one approved development admin account.

This script is for local development only. Configure DEV_ADMIN_* values in .env
before running it; never use the defaults in production.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import User

Base.metadata.create_all(bind=engine)

username = os.getenv("DEV_ADMIN_USERNAME", "admin")
email = os.getenv("DEV_ADMIN_EMAIL", "admin@example.com")
password = os.getenv("DEV_ADMIN_PASSWORD", "ChangeMe123!")
full_name = os.getenv("DEV_ADMIN_FULL_NAME", "Development Administrator")

db = SessionLocal()
try:
    user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if user is None:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role="ADMIN",
            is_active=True,
            is_approved=True,
        )
        db.add(user)
        db.commit()
        print(f"Created development admin: {email}")
    else:
        print(f"Development admin already exists: {user.email}")
finally:
    db.close()
