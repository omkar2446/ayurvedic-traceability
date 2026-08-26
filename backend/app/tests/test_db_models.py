from app.database import Base, engine
from app.models import Organization, User, HerbBatch


def test_model_metadata_can_be_created() -> None:
    metadata_tables = set(Base.metadata.tables.keys())
    assert "organizations" in metadata_tables
    assert "users" in metadata_tables
    assert "herb_batches" in metadata_tables
    assert "custody_transfers" in metadata_tables
    assert "lab_reports" in metadata_tables
    assert "products" in metadata_tables


def test_engine_is_configured() -> None:
    assert engine is not None
    assert "postgresql" in str(engine.url)
