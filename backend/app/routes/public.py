from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_db
from app.models import CustodyTransfer, HerbBatch, LabReport, ProcessingRecord, Product, ProductBatch

router = APIRouter(prefix="/api/public", tags=["public"])


class PublicProductTraceability(BaseModel):
    product_id: str
    product_name: str
    manufacturer_name: Optional[str] = None
    manufacturing_date: datetime
    batch_id: str
    herb_name: str
    collection_location: str
    collection_date: datetime
    transfers: list[dict]
    processing: list[dict]
    lab_reports: list[dict]


@router.get("/verify/{identifier}", response_model=PublicProductTraceability)
def verify_identifier(
    identifier: str,
    db: Session = Depends(get_db),
):
    identifier_clean = identifier.strip()

    # Try product first
    product = db.query(Product).filter(func.lower(Product.product_id) == identifier_clean.lower()).first()

    batch = None
    if product:
        product_batch = db.query(ProductBatch).filter(ProductBatch.product_id == product.product_id).first()
        if product_batch:
            batch = db.query(HerbBatch).filter(HerbBatch.batch_id == product_batch.batch_id).first()
    else:
        # Search by Batch ID
        batch = db.query(HerbBatch).filter(func.lower(HerbBatch.batch_id) == identifier_clean.lower()).first()
        if batch:
            product_batch = db.query(ProductBatch).filter(ProductBatch.batch_id == batch.batch_id).first()
            if product_batch:
                product = db.query(Product).filter(Product.product_id == product_batch.product_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="No public traceability record found for this identifier")

    transfers_db = db.query(CustodyTransfer).filter(
        CustodyTransfer.batch_id == batch.batch_id,
        CustodyTransfer.status == "ACCEPTED"
    ).order_by(CustodyTransfer.created_at.asc()).all()
    transfers = [{"id": t.id, "quantity": t.quantity, "date": t.updated_at or t.created_at} for t in transfers_db]

    processing_db = db.query(ProcessingRecord).filter(
        ProcessingRecord.batch_id == batch.batch_id
    ).order_by(ProcessingRecord.created_at.asc()).all()
    processing = [{"id": p.id, "input": p.input_quantity, "output": p.output_quantity, "date": p.processing_date or p.created_at} for p in processing_db]

    lab_reports_db = db.query(LabReport).filter(
        LabReport.batch_id == batch.batch_id
    ).order_by(LabReport.created_at.asc()).all()
    lab_reports = [{"certificate_id": l.certificate_id, "result": l.result, "date": l.test_date or l.created_at} for l in lab_reports_db]

    return {
        "product_id": product.product_id if product else batch.batch_id,
        "product_name": product.name if product else f"{batch.herb_name} Organic Batch",
        "manufacturer_name": "VanaTrace Certified Partner",
        "manufacturing_date": product.created_at if product else batch.created_at,
        "batch_id": batch.batch_id,
        "herb_name": batch.herb_name,
        "collection_location": batch.collection_location,
        "collection_date": batch.collection_date or batch.created_at,
        "transfers": transfers,
        "processing": processing,
        "lab_reports": lab_reports
    }
