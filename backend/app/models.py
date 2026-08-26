from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DECIMAL as Decimal

from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdentityVerification(Base):
    __tablename__ = "identity_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)
    document_reference = Column(String(255), nullable=True)
    verification_status = Column(String(50), nullable=False, default="PENDING", index=True)
    verification_details = Column(JSON, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)


class HerbBatch(Base):
    __tablename__ = "herb_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), unique=True, nullable=False, index=True)
    herb_name = Column(String(255), nullable=False)
    scientific_name = Column(String(255), nullable=False)
    quantity = Column(Decimal(18, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    collection_date = Column(DateTime, nullable=False)
    collection_location = Column(String(255), nullable=False)
    latitude = Column(Decimal(9, 6), nullable=True)
    longitude = Column(Decimal(9, 6), nullable=True)
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    initial_holder_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    current_holder_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    source_type = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="CREATED")
    recall_status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustodyTransfer(Base):
    __tablename__ = "custody_transfers"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), ForeignKey("herb_batches.batch_id"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    quantity = Column(Decimal(18, 2), nullable=False)
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    certificate_prefix = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(100), unique=True, nullable=False)
    batch_id = Column(String(100), ForeignKey("herb_batches.batch_id"), nullable=False)
    laboratory_id = Column(Integer, ForeignKey("laboratories.id"), nullable=True)
    report_hash = Column(String(255), nullable=False)
    result = Column(String(50), nullable=False)
    report_url = Column(Text, nullable=True)
    test_type = Column(String(255), nullable=True)
    test_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProcessingRecord(Base):
    __tablename__ = "processing_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), ForeignKey("herb_batches.batch_id"), nullable=False)
    processor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    input_quantity = Column(Decimal(18, 2), nullable=False)
    output_quantity = Column(Decimal(18, 2), nullable=False)
    loss_quantity = Column(Decimal(18, 2), nullable=False)
    processing_details = Column(Text, nullable=True)
    processing_location = Column(String(255), nullable=True)
    processing_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    manufacturer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), ForeignKey("products.product_id"), nullable=False)
    batch_id = Column(String(100), ForeignKey("herb_batches.batch_id"), nullable=False)
    quantity_used = Column(Decimal(18, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recall(Base):
    __tablename__ = "recalls"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), ForeignKey("herb_batches.batch_id"), nullable=False)
    reason = Column(Text, nullable=False)
    recall_date = Column(DateTime, nullable=False)
    authorized_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(150), nullable=False)
    entity_type = Column(String(150), nullable=True)
    entity_id = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String(255), unique=True, nullable=True)
    event_type = Column(String(150), nullable=False)
    batch_id = Column(String(100), nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SuspiciousEvent(Base):
    __tablename__ = "suspicious_events"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), nullable=True)
    event_type = Column(String(150), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN")
    timestamp = Column(DateTime, default=datetime.utcnow)
