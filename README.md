# MxSense Edge AI Console

This repo now mirrors the product idea from the provided MxSense Edge AI Server PDF and workbook while keeping the implementation in Django + DRF for the backend and Next.js for the frontend.

## Product Modules

- Operations Dashboard
- Devices & Assets
- Connectivity & Adaptation
- Data Collection & Sessions
- Preprocessing & Feature Engineering
- Inferencing & Fusion
- Quality / Decision Intelligence
- Alerts & Incidents
- Monitoring & Performance
- Storage & Retention
- API Gateway & Integrations
- Edge-to-Cloud Sync
- Admin / Security / Governance

## Backend Apps

- `backend/apps/device_manager`: sites, devices, channels, configs, firmware jobs, lifecycle events
- `backend/apps/data_ingestion`: sensors, calibration profiles, batches, samples, sessions, raw readings, image captures
- `backend/apps/mqtt_service`: protocol adapters, MQTT topics, schema mappings, message logs
- `backend/apps/ai_orchestration`: preprocessing profiles, processed records, feature vectors, models, inference jobs/results
- `backend/apps/quality_center`: decision rules, quality scores, notification routes, alerts, human reviews
- `backend/apps/monitoring`: service health, telemetry, metrics, logs, incidents
- `backend/apps/storage_sync`: storage artifacts, retention policies, backup jobs, sync jobs
- `backend/apps/governance`: roles, policies, approvals, audit logs, secret credentials
- `backend/apps/api_gateway`: overview, blueprint, endpoint registry, request logs

## Frontend

The frontend lives in `frontend/` as a Next.js operations console shell. It reads from:

- `/api/api-gateway/overview/`
- `/api/api-gateway/blueprint/`

If the backend is not running, it falls back to local blueprint data so the UI still renders.

## Run

Backend:

```bash
cd backend
venv/bin/python manage.py runserver 0.0.0.0:8000
```

### Configure AWS RDS (PostgreSQL) and create tables

1) Copy env template and fill AWS RDS values:

```bash
cd backend
cp .env.example .env
```

Set these in `.env`:

- `DB_ENGINE=django.db.backends.postgresql`
- `DB_NAME=<your_rds_db_name>`
- `DB_USER=<your_rds_user>`
- `DB_PASSWORD=<your_rds_password>`
- `DB_HOST=<your_rds_endpoint>`
- `DB_PORT=5432`
- `DB_SSLMODE=require` (recommended for RDS)
- `DB_CONNECT_TIMEOUT=10`

2) Install deps and run migrations:

```bash
cd backend
venv/bin/pip install -r requirements.txt
venv/bin/python manage.py migrate
```

This creates all required web app tables in RDS (device management, data ingestion, monitoring, auth, etc.).

Frontend:

```bash
cd frontend
npm install
npm run dev
```
