CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS herb_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    herb_name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(18, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    collection_date TIMESTAMP NOT NULL,
    collection_location VARCHAR(255) NOT NULL,
    latitude DECIMAL(9, 6),
    longitude DECIMAL(9, 6),
    collector_id INTEGER REFERENCES users(id),
    initial_holder_id INTEGER REFERENCES users(id),
    source_type VARCHAR(100),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'CREATED',
    recall_status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS custody_transfers (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL REFERENCES herb_batches(batch_id),
    from_user_id INTEGER REFERENCES users(id),
    to_user_id INTEGER REFERENCES users(id),
    quantity DECIMAL(18, 2) NOT NULL,
    location VARCHAR(255),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS laboratories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    certificate_prefix VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lab_reports (
    id SERIAL PRIMARY KEY,
    certificate_id VARCHAR(100) UNIQUE NOT NULL,
    batch_id VARCHAR(100) NOT NULL REFERENCES herb_batches(batch_id),
    laboratory_id INTEGER REFERENCES laboratories(id),
    report_hash VARCHAR(255) NOT NULL,
    result VARCHAR(50) NOT NULL,
    report_url TEXT,
    test_type VARCHAR(255),
    test_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processing_records (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL REFERENCES herb_batches(batch_id),
    processor_id INTEGER REFERENCES users(id),
    input_quantity DECIMAL(18, 2) NOT NULL,
    output_quantity DECIMAL(18, 2) NOT NULL,
    loss_quantity DECIMAL(18, 2) NOT NULL,
    processing_details TEXT,
    processing_location VARCHAR(255),
    processing_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manufacturer_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_batches (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL REFERENCES products(product_id),
    batch_id VARCHAR(100) NOT NULL REFERENCES herb_batches(batch_id),
    quantity_used DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recalls (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL REFERENCES herb_batches(batch_id),
    reason TEXT NOT NULL,
    recall_date TIMESTAMP NOT NULL,
    authorized_by INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(150) NOT NULL,
    entity_type VARCHAR(150),
    entity_id VARCHAR(150),
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blockchain_transactions (
    id SERIAL PRIMARY KEY,
    tx_id VARCHAR(255) UNIQUE,
    event_type VARCHAR(150) NOT NULL,
    batch_id VARCHAR(100),
    payload JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS suspicious_events (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100),
    event_type VARCHAR(150) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
