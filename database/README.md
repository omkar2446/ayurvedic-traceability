# Ayurvedic Traceability Database

This folder owns the PostgreSQL schema and Alembic migration history for the Ayurvedic traceability backend.

## Phase 1 scope

Phase 1 configures PostgreSQL, SQLAlchemy 2.x, and Alembic. The initial migration is intentionally empty. Domain tables are added in later phases in dependency order.

## Connection

The backend reads `DATABASE_URL` from `backend/.env`. Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ayurvedic_traceability
```

If `DATABASE_URL` is omitted, the backend builds the same URL from the `POSTGRES_*` settings.

SQLAlchemy creates one engine with connection pre-pinging enabled. Application code obtains sessions from `SessionLocal`; each session must be closed by its caller or dependency.

## PostgreSQL setup

Install PostgreSQL 15 or newer, then create a development database:

```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE ayurvedic_traceability OWNER postgres;
```

Do not use these credentials in production. Keep `backend/.env` out of source control.

## Migrations

From the repository root, after installing backend dependencies:

```powershell
cd d:\ayurvedic-traceability
.\backend\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Generate a future migration after adding reviewed SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "add organizations and users"
```

Review generated SQL before applying it. Roll back one revision with:

```powershell
alembic downgrade -1
```

The current Phase 1 revision creates no domain tables.

## Verify connection

Run the backend and request:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

`database` is `healthy` only when PostgreSQL responds to `SELECT 1`.

## Privacy

The database will store searchable application state and secure document references, never plaintext passwords or blockchain private keys. Public traceability must be built from explicitly approved fields and must not expose identity documents or private contact details.
