
import os
import sys

# Ensure backend root directory is in sys.path for Render deployment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.batches import router as batches_router
from app.routes.transfers import router as transfers_router
from app.routes.processing import router as processing_router
from app.routes.laboratory import router as laboratory_router
from app.routes.products import router as products_router
from app.routes.public import router as public_router
from app.routes.users import router as users_router
from app import models

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
] + [origin.strip() for origin in settings.backend_cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(batches_router)
app.include_router(transfers_router)
app.include_router(processing_router)
app.include_router(laboratory_router)
app.include_router(products_router)
app.include_router(public_router)
app.include_router(users_router)


@app.on_event("startup")
def initialize_development_database() -> None:
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        _migrate_development_sqlite()
        try:
            from seed_dummy_products import seed_demo_data
            seed_demo_data()
        except Exception as e:
            print("Auto-seed info:", e)


def _migrate_development_sqlite() -> None:
    inspector = inspect(engine)
    herb_batch_columns = {column["name"] for column in inspector.get_columns("herb_batches")}
    if "current_holder_id" not in herb_batch_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE herb_batches ADD COLUMN current_holder_id INTEGER"))


@app.get("/api/health", tags=["health"])
def health_check() -> dict[str, str]:
    database_status = "healthy"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        database_status = "unavailable"

    return {
        "api": "healthy",
        "database": database_status,
        "blockchain": "unavailable",
    }


@app.get("/health", include_in_schema=False)
def legacy_health_check() -> dict[str, str]:
    return health_check()
