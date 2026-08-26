# Ayurvedic Traceability Backend

Phase 1 provides the FastAPI application, PostgreSQL connection configuration, and infrastructure health endpoint. Authentication, models, migrations, and Fabric transactions are added in later phases.

## Requirements

- Python 3.11 or newer
- PostgreSQL 14 or newer

## Local setup

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Create the PostgreSQL database with `psql`:

```sql
CREATE USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE ayurvedic_traceability OWNER postgres;
```

Use a different database user/password in `.env` for a real deployment. Never commit `.env` or production secrets.

## Run

```powershell
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for generated API documentation.

## Development login

The database starts empty. Create an approved development administrator with:

```powershell
$env:DEV_ADMIN_EMAIL = "admin@example.com"
$env:DEV_ADMIN_PASSWORD = "ChangeMe123!"
python scripts/seed_dev_admin.py
```

Then use that email and password in the frontend login form. This account and password are for development only.

## Health check

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

With PostgreSQL running, the response is:

```json
{"api":"healthy","database":"healthy","blockchain":"unavailable"}
```

Blockchain is intentionally reported as `unavailable` until the Fabric integration phase. The API never claims a Fabric connection that has not been established.

## Docker

```powershell
docker build -t ayurvedic-traceability-backend .
docker run --rm -p 8000:8000 --env-file .env ayurvedic-traceability-backend
```
