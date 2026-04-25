# Device Management Web App (MXSense)

React + Django app for monitoring sensor telemetry coming from edge devices via MQTT (AWS IoT Core), storing it in PostgreSQL (AWS RDS), and streaming real-time updates to the browser via WebSockets.

## Repo layout

- `backend/`: Django + DRF + Channels (WebSocket)
- `frontend/`: React (Vite) + Tailwind + Recharts

## Backend setup (Django)

### 1) Create `.env`

Copy the example and fill values:

```bash
cp backend/.env.example backend/.env
```

Required:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `DJANGO_SECRET_KEY`

Optional (recommended for WebSockets at scale):
- `REDIS_URL=redis://localhost:6379/0`

### 2) Install Python deps

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

### 3) Run migrations (for auth tables)

This creates Django auth tables inside your configured PostgreSQL database (`mxsense_db`).

```bash
source backend/.venv/bin/activate
cd backend
python manage.py migrate
```

### 4) Run the server (HTTP + WebSocket)

Dev server:

```bash
source backend/.venv/bin/activate
cd backend
python manage.py runserver 0.0.0.0:8000
```

Production-style ASGI server:

```bash
source backend/.venv/bin/activate
cd backend
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### 5) (Optional) Start Redis for Channels

If you set `REDIS_URL`, start Redis:

```bash
cd backend
docker compose up -d
```

## Frontend setup (React)

### 1) Create `.env`

```bash
cp frontend/.env.example frontend/.env
```

Defaults:
- API: `http://localhost:8000`
- WS: `ws://localhost:8000`

### 2) Install deps + run

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API endpoints

### Auth

- `POST /api/auth/register/` `{ "username": "...", "email": "...", "password": "..." }`
- `POST /api/auth/login/` `{ "username": "...", "password": "..." }` → `{ access, refresh }`
- `POST /api/auth/token/refresh/` `{ "refresh": "..." }`

### Ingestion (from AWS IoT / Lambda)

- `POST /api/ingest/` (no auth by default)

Example:

```bash
curl -X POST http://localhost:8000/api/ingest/ \
  -H 'Content-Type: application/json' \
  -d @sample.json
```

### Device + dashboard APIs (JWT required)

- `GET /api/devices/`
- `GET /api/devices/{device_id}/`
- `GET /api/devices/{device_id}/sensor/{type}/?start=...&end=...&limit=...`
- `GET /api/devices/{device_id}/health/?start=...&end=...&limit=...`
- `GET /api/dashboard/summary/`

Sensor `type` values:
`env`, `voc`, `gas`, `pm`, `spectral`, `force`, `flow`, `system`, `acoustic`, `distance`

## WebSocket endpoints

- `ws://{host}/ws/dashboard/` (all devices)
- `ws://{host}/ws/device/{device_id}/` (single device)

Payload is emitted after ingestion as:

```json
{
  "device_id": "MX-ORIN-NX-001",
  "timestamp": "2026-03-17T02:05:00+00:00",
  "payload": { "...original JSON..." }
}
```

## Notes / gotchas

- The sensor tables are modeled with `managed = False` in Django, so Django will **not** create or modify your existing telemetry tables.
- If your existing RDS tables have additional/different columns, update `backend/devices/models.py` to match the exact schema.
- For production ingestion from AWS IoT Core, typically you’ll use an **IoT Rule → Lambda** (or HTTP action) that forwards the JSON to `POST /api/ingest/`.

