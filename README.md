# 🐷 FarmaTrack

Pig farm management system — herd tracking, health records, farrowing logs & ear-tag OCR scanning.

**Stack:** FastAPI · SQLAlchemy · Streamlit · Tesseract OCR · SQLite

## Pig Categories

| Category | Description |
|----------|-------------|
| Piglet | Newborn to weaning |
| Finisher | Growing pigs for market |
| Gilt | Young female, pre-first-farrowing |
| Sow | Breeding female (AI only — no boar) |

## Quick Start

```bash
# 1. Clone & install
git clone <repo-url> && cd farmatrack
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env   # edit if needed

# 3. Seed demo data (optional)
python -m database.seed

# 4. Start API (terminal 1)
uvicorn main:app --reload --port 8000

# 5. Start Dashboard (terminal 2)
streamlit run dashboard/app.py --server.port 8501
```

## API Endpoints

| Route | Description |
|-------|-------------|
| `GET/POST /pigs/` | List / create pigs |
| `GET/PATCH/DELETE /pigs/{id}` | Read / update / deactivate pig |
| `GET/POST /health/` | Health records |
| `GET/POST /farrowings/` | Farrowing records |
| `GET/POST /pens/` | Pen management with occupancy |
| `POST /scan/` | Manual ear-tag scan |
| `POST /scan/image` | OCR image scan |
| `GET /scan/logs` | Scan history |
| `GET /dashboard/summary` | Aggregated stats |

Interactive docs at `http://localhost:8000/docs`.

## Tests

```bash
pytest tests/ -v
```

## Project Structure

```
farmatrack/
├── main.py                  # FastAPI entry
├── config.py                # Settings (.env)
├── database/
│   ├── models.py            # ORM models
│   ├── enums.py             # PigCategory, HealthStatus, ScanSource
│   ├── connection.py        # Engine, session, get_db
│   └── seed.py              # Demo data seeder
├── schemas/                 # Pydantic request/response
├── services/                # Business logic
├── scanner/ocr.py           # Tesseract OCR wrapper
├── routers/                 # FastAPI route handlers
├── dashboard/
│   ├── app.py               # Streamlit entry (sidebar nav)
│   ├── api_client.py        # HTTP wrapper for API calls
│   ├── pages/               # 6 Streamlit pages
│   └── components/          # Reusable UI (pig_card, status_badge)
└── tests/                   # Pytest suite
```
