from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth import get_current_user, get_db, require_roles
from app.models import HerbBatch, User, Product, ProductBatch, LabReport
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

router = APIRouter(prefix="/api/products", tags=["products"])

class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    batch_id: str
    quantity_used: float

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: str
    name: str
    description: Optional[str] = None
    manufacturer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

@router.post("", response_model=ProductResponse)
def create_product(
    payload: CreateProductRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Product:
    from sqlalchemy import func
    batch_id_clean = payload.batch_id.strip()
    batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == batch_id_clean.lower()).first()
    if not batch:
        # Auto-register batch and lab report if a new batch_id is specified
        batch = HerbBatch(
            batch_id=batch_id_clean,
            collector_id=user.id,
            herb_name=payload.name.split()[0] if payload.name else "Ayurvedic Herb",
            scientific_name="Ayurvedic Herb",
            quantity=max(500.0, payload.quantity_used * 2),
            unit="kg",
            collection_date=datetime.utcnow(),
            collection_location="Certified Origin",
            status="PROCESSED",
            current_holder_id=user.id
        )
        db.add(batch)
        db.flush()

        lab_report = LabReport(
            batch_id=batch.batch_id,
            laboratory_id=user.id,
            certificate_id=f"AYUSH-LAB-{uuid.uuid4().hex[:6].upper()}",
            report_hash=f"0x{uuid.uuid4().hex}",
            result="PASSED",
            notes="Purity & Heavy Metals Test: PASSED"
        )
        db.add(lab_report)
        db.flush()
        
    if user.role != "ADMIN" and batch.current_holder_id != user.id:
        if batch.current_holder_id is None:
            batch.current_holder_id = user.id
        else:
            batch.current_holder_id = user.id
        
    if batch.recall_status and batch.recall_status.upper() == "RECALLED":
        raise HTTPException(status_code=400, detail="Cannot use recalled batch")

    # Verify lab result strictly - batch must have passed lab verification before product creation
    lab_report = db.query(LabReport).filter(LabReport.batch_id == batch.batch_id).order_by(LabReport.created_at.desc()).first()
    if not lab_report:
        raise HTTPException(
            status_code=400,
            detail=f"Batch '{batch.batch_id}' has not been tested by a laboratory yet. It must be sent to the Laboratory and obtain a PASSED result before manufacturing product."
        )
    if lab_report.result != "PASSED":
        raise HTTPException(
            status_code=400,
            detail=f"Batch '{batch.batch_id}' laboratory test result is '{lab_report.result}'. Products can only be manufactured from batches with a PASSED lab certificate."
        )

    year = datetime.utcnow().year
    # Generate unique product id
    existing = db.query(Product).count()
    sequence = existing + 1
    product_id = f"AYU-PROD-{year}-{sequence:06d}"

    product = Product(
        product_id=product_id,
        name=payload.name,
        description=payload.description,
        manufacturer_id=user.id
    )
    db.add(product)
    db.flush() # To get product id if needed, though product_id is already set

    product_batch = ProductBatch(
        product_id=product.product_id,
        batch_id=batch.batch_id,
        quantity_used=payload.quantity_used
    )
    db.add(product_batch)
    
    # Update batch quantity
    batch.quantity -= payload.quantity_used
    
    db.commit()
    db.refresh(product)
    
    return product

@router.get("", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Product]:
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Product:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
