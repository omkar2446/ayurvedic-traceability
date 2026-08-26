import os
import sys
from datetime import datetime, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import User, HerbBatch, CustodyTransfer, ProcessingRecord, LabReport, Product, ProductBatch
from app.auth import hash_password

def seed_demo_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("🌱 Seeding Users...")
        users_data = [
            {"username": "collector1", "email": "collector@vanatrace.org", "full_name": "Ramesh Kumar (Wild Harvester)", "role": "COLLECTOR"},
            {"username": "aggregator1", "email": "aggregator@vanatrace.org", "full_name": "Kerala Herbal Co-op", "role": "AGGREGATOR"},
            {"username": "processor1", "email": "processor@vanatrace.org", "full_name": "BioExtract Phytochemicals", "role": "PROCESSOR"},
            {"username": "lab1", "email": "lab@vanatrace.org", "full_name": "Ayush Certified Testing Lab", "role": "LABORATORY"},
            {"username": "manufacturer1", "email": "manufacturer@vanatrace.org", "full_name": "VedaLife Remedies Ltd", "role": "MANUFACTURER"},
        ]

        user_instances = {}
        for ud in users_data:
            user = db.query(User).filter(User.username == ud["username"]).first()
            if not user:
                user = User(
                    username=ud["username"],
                    email=ud["email"],
                    password_hash=hash_password("Password123!"),
                    full_name=ud["full_name"],
                    role=ud["role"],
                    is_active=True,
                    is_approved=True
                )
                db.add(user)
                db.flush()
            user_instances[ud["role"]] = user

        db.commit()

        print("🌿 Seeding 10 Complete Ayurvedic Products...")
        
        dummies = [
            {
                "batch_id": "ASHW-2026-000001",
                "herb_name": "Ashwagandha",
                "scientific_name": "Withania somnifera",
                "quantity": 100.0,
                "unit": "kg",
                "location": "Wayanad Forests, Kerala, India",
                "lat": 11.6854,
                "lng": 76.1320,
                "prod_id": "AYU-PROD-2026-000001",
                "prod_name": "Organic Ashwagandha Root Extract 500mg",
                "prod_desc": "Standardized to 5% Withanolides for stress resilience and vitality.",
                "cert_id": "AYUSH-LAB-2026-9901",
                "process_type": "Supercritical CO2 Extraction",
                "notes": "Purity 99.4% | Heavy Metals: Passed | Microbes: Clear"
            },
            {
                "batch_id": "TULS-2026-000002",
                "herb_name": "Holy Basil (Tulsi)",
                "scientific_name": "Ocimum sanctum",
                "quantity": 60.0,
                "unit": "kg",
                "location": "Vrindavan Botanical Reserve, UP, India",
                "lat": 27.5706,
                "lng": 77.7006,
                "prod_id": "AYU-PROD-2026-000002",
                "prod_name": "Pure Sacred Tulsi Immunity Drops",
                "prod_desc": "Concentrated liquid extract of Krishna and Rama Tulsi leaves.",
                "cert_id": "AYUSH-LAB-2026-9902",
                "process_type": "Hydro-Distillation Extraction",
                "notes": "Essential Oil Content: 1.8% | Eugenol Verified"
            },
            {
                "batch_id": "SHAT-2026-000003",
                "herb_name": "Shatavari",
                "scientific_name": "Asparagus racemosus",
                "quantity": 80.0,
                "unit": "kg",
                "location": "Satpura Tiger Reserve Fringe, MP, India",
                "lat": 22.4674,
                "lng": 78.4350,
                "prod_id": "AYU-PROD-2026-000003",
                "prod_name": "Shatavari Hormone & Wellness Tonic",
                "prod_desc": "Wildcrafted root extract promoting female reproductive health and hormonal balance.",
                "cert_id": "AYUSH-LAB-2026-9903",
                "process_type": "Aqueous Decoction & Vacuum Drying",
                "notes": "Saponin Assay: 22% Shatavarins | Passed Grade A"
            },
            {
                "batch_id": "BRAH-2026-000004",
                "herb_name": "Brahmi",
                "scientific_name": "Bacopa monnieri",
                "quantity": 45.0,
                "unit": "kg",
                "location": "Sundarbans Wetland Ecosystem, West Bengal",
                "lat": 21.9497,
                "lng": 89.1833,
                "prod_id": "AYU-PROD-2026-000004",
                "prod_name": "Brahmi Memory & Cognitive Syrup",
                "prod_desc": "Traditional Nootropic formulation for focus, clarity, and neurological health.",
                "cert_id": "AYUSH-LAB-2026-9904",
                "process_type": "Fresh Leaf Juice Freeze Drying",
                "notes": "Bacoside A&B Content: 20% | Pesticide Residue: Zero"
            },
            {
                "batch_id": "TRIP-2026-000005",
                "herb_name": "Triphala (Haritaki, Bibhitaki, Amalaki)",
                "scientific_name": "Terminalia chebula mix",
                "quantity": 120.0,
                "unit": "kg",
                "location": "Western Ghats Biodiversity Zone, Karnataka",
                "lat": 13.1365,
                "lng": 75.3255,
                "prod_id": "AYU-PROD-2026-000005",
                "prod_name": "Triphala Digestive & Detox Powder",
                "prod_desc": "Equal ratio blend of 3 sacred fruits for gentle colon cleansing and digestion.",
                "cert_id": "AYUSH-LAB-2026-9905",
                "process_type": "Micro-Milling & Sieve Pulverization",
                "notes": "Tannins Content: 35% | Particle Size: 80 Mesh"
            },
            {
                "batch_id": "NEEM-2026-000006",
                "herb_name": "Neem",
                "scientific_name": "Azadirachta indica",
                "quantity": 75.0,
                "unit": "kg",
                "location": "Jodhpur Organic Zone, Rajasthan",
                "lat": 26.2389,
                "lng": 73.0243,
                "prod_id": "AYU-PROD-2026-000006",
                "prod_name": "Neem Blood Purifier & Skin Elixir",
                "prod_desc": "Cold-pressed organic Neem leaf & seed extract for clear skin and detox.",
                "cert_id": "AYUSH-LAB-2026-9906",
                "process_type": "Cold Solvent-Free Pressing",
                "notes": "Azadirachtin Assay: 1500ppm | Certified Organic"
            },
            {
                "batch_id": "GUDU-2026-000007",
                "herb_name": "Guduchi (Giloy)",
                "scientific_name": "Tinospora cordifolia",
                "quantity": 90.0,
                "unit": "kg",
                "location": "Haridwar Foothills, Uttarakhand",
                "lat": 29.9457,
                "lng": 78.1642,
                "prod_id": "AYU-PROD-2026-000007",
                "prod_name": "Giloy Ghanvati Pure Satva Tablets",
                "prod_desc": "Concentrated stem satva extract for immunomodulation and fever management.",
                "cert_id": "AYUSH-LAB-2026-9907",
                "process_type": "Stem Starch Water Extraction (Satva)",
                "notes": "Bitters Assay: PASSED | Microbial Count: <10 CFU/g"
            },
            {
                "batch_id": "HARI-2026-000008",
                "herb_name": "Wild Turmeric (Haridra)",
                "scientific_name": "Curcuma longa",
                "quantity": 150.0,
                "unit": "kg",
                "location": "Kandhamal Valley, Odisha",
                "lat": 20.2374,
                "lng": 84.1442,
                "prod_id": "AYU-PROD-2026-000008",
                "prod_name": "High Potency Curcumin C3 Complex",
                "prod_desc": "Organic high-curcumin turmeric rhizome extract with piperine bio-enhancer.",
                "cert_id": "AYUSH-LAB-2026-9908",
                "process_type": "Solvent Crystallization & Standardization",
                "notes": "Curcuminoids Assay: 95% Pure | Heavy Metals: ND"
            },
            {
                "batch_id": "AMLA-2026-000009",
                "herb_name": "Amalaki (Indian Gooseberry)",
                "scientific_name": "Phyllanthus emblica",
                "quantity": 110.0,
                "unit": "kg",
                "location": "Pratapgarh Orchards, Uttar Pradesh",
                "lat": 25.9248,
                "lng": 81.9866,
                "prod_id": "AYU-PROD-2026-000009",
                "prod_name": "Natural Vitamin C Amla Concentrate",
                "prod_desc": "Rich source of natural Vitamin C and polyphenols for anti-aging and vitality.",
                "cert_id": "AYUSH-LAB-2026-9909",
                "process_type": "Cold Vacuum Evaporation Juicing",
                "notes": "Natural Ascorbic Acid: 600mg/100g | PASSED"
            },
            {
                "batch_id": "SHAN-2026-000010",
                "herb_name": "Shankhpushpi",
                "scientific_name": "Convolvulus pluricaulis",
                "quantity": 40.0,
                "unit": "kg",
                "location": "Aravalli Range, Haryana",
                "lat": 28.3802,
                "lng": 77.0545,
                "prod_id": "AYU-PROD-2026-000010",
                "prod_name": "Shankhpushpi Mind Reliever & Sleep Elixir",
                "prod_desc": "Synergistic Medhya Rasayana herb for anxiety reduction and restful sleep.",
                "cert_id": "AYUSH-LAB-2026-9910",
                "process_type": "Whole Plant Decoction & Spray Drying",
                "notes": "Alkaloids Content: 0.5% | Heavy Metals: Passed"
            }
        ]

        now = datetime.utcnow()

        for i, d in enumerate(dummies):
            # 1. Herb Batch
            batch = db.query(HerbBatch).filter(HerbBatch.batch_id == d["batch_id"]).first()
            if not batch:
                batch = HerbBatch(
                    batch_id=d["batch_id"],
                    herb_name=d["herb_name"],
                    scientific_name=d["scientific_name"],
                    quantity=d["quantity"],
                    unit=d["unit"],
                    collection_date=now - timedelta(days=30 - i),
                    collection_location=d["location"],
                    latitude=d["lat"],
                    longitude=d["lng"],
                    collector_id=user_instances["COLLECTOR"].id,
                    initial_holder_id=user_instances["COLLECTOR"].id,
                    current_holder_id=user_instances["MANUFACTURER"].id,
                    source_type="ORGANIC_FARMING" if i % 2 == 0 else "WILD_HARVEST",
                    notes=f"Harvested during peak potency stage. {d['notes']}",
                    status="ACCEPTED",
                    recall_status="ACTIVE"
                )
                db.add(batch)
                db.flush()

            # 2. Custody Transfers
            t1 = db.query(CustodyTransfer).filter(CustodyTransfer.batch_id == d["batch_id"]).first()
            if not t1:
                db.add(CustodyTransfer(
                    batch_id=d["batch_id"],
                    from_user_id=user_instances["COLLECTOR"].id,
                    to_user_id=user_instances["AGGREGATOR"].id,
                    quantity=d["quantity"],
                    notes="Transferred from harvester to local regional co-op hub",
                    status="ACCEPTED",
                    created_at=now - timedelta(days=25 - i),
                    updated_at=now - timedelta(days=24 - i)
                ))
                db.add(CustodyTransfer(
                    batch_id=d["batch_id"],
                    from_user_id=user_instances["AGGREGATOR"].id,
                    to_user_id=user_instances["PROCESSOR"].id,
                    quantity=d["quantity"],
                    notes=f"Dispatched for processing: {d['process_type']}",
                    status="ACCEPTED",
                    created_at=now - timedelta(days=20 - i),
                    updated_at=now - timedelta(days=19 - i)
                ))
                db.add(CustodyTransfer(
                    batch_id=d["batch_id"],
                    from_user_id=user_instances["PROCESSOR"].id,
                    to_user_id=user_instances["MANUFACTURER"].id,
                    quantity=d["quantity"],
                    notes="Delivered to WHO-GMP certified manufacturing cleanroom",
                    status="ACCEPTED",
                    created_at=now - timedelta(days=10 - i),
                    updated_at=now - timedelta(days=9 - i)
                ))

            # 3. Processing Record
            proc = db.query(ProcessingRecord).filter(ProcessingRecord.batch_id == d["batch_id"]).first()
            if not proc:
                in_qty = d["quantity"]
                out_qty = round(d["quantity"] * 0.82, 2)
                loss_qty = round(in_qty - out_qty, 2)
                db.add(ProcessingRecord(
                    batch_id=d["batch_id"],
                    processor_id=user_instances["PROCESSOR"].id,
                    processing_details=d["process_type"],
                    input_quantity=in_qty,
                    output_quantity=out_qty,
                    loss_quantity=loss_qty,
                    processing_location="BioExtract Phytochemicals Plant #1",
                    processing_date=now - timedelta(days=15 - i),
                    status="COMPLETED"
                ))

            # 4. Lab Report
            lab = db.query(LabReport).filter(LabReport.batch_id == d["batch_id"]).first()
            if not lab:
                db.add(LabReport(
                    batch_id=d["batch_id"],
                    lab_user_id=user_instances["LABORATORY"].id,
                    certificate_id=d["cert_id"],
                    result="PASSED",
                    test_date=now - timedelta(days=12 - i),
                    report_url="https://vanatrace.org/certificates/" + d["cert_id"],
                    notes=d["notes"]
                ))

            # 5. Product & ProductBatch linkage
            prod = db.query(Product).filter(Product.product_id == d["prod_id"]).first()
            if not prod:
                prod = Product(
                    product_id=d["prod_id"],
                    name=d["prod_name"],
                    description=d["prod_desc"],
                    manufacturer_id=user_instances["MANUFACTURER"].id,
                    created_at=now - timedelta(days=5 - i)
                )
                db.add(prod)
                db.flush()

                db.add(ProductBatch(
                    product_id=prod.product_id,
                    batch_id=d["batch_id"],
                    quantity_used=round(d["quantity"] * 0.25, 2)
                ))

        db.commit()
        print("✅ 10 Complete Ayurvedic Products Seeded Successfully!")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding data:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
