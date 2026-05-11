# FarmaTrack — Claude Code Context

Pig farm management system for **Veliki Jarak** farm. Built with FastAPI + Streamlit + SQLAlchemy.

---

## How to run locally

```bash
# Always use Python 3.9 — system python3 (3.14) does NOT have dependencies installed
/opt/homebrew/bin/python3.9 -m uvicorn main:app --reload --port 8000   # Terminal 1
streamlit run dashboard/app.py                                           # Terminal 2

# Run tests
/opt/homebrew/bin/python3.9 -m pytest tests/ -v

# Seed demo data (run once)
/opt/homebrew/bin/python3.9 -c "from database.seed import seed; seed()"
```

---

## Project structure

```
farmatrack/
├── main.py                  # FastAPI app entry point (kept for future API use)
├── config.py                # Settings via pydantic-settings, reads .env
├── requirements.txt
├── packages.txt             # System deps for Streamlit Cloud (tesseract-ocr)
│
├── database/
│   ├── models.py            # SQLAlchemy ORM: Pen, Pig, HealthRecord, Farrowing, ScanLog
│   ├── enums.py             # PigCategory, HealthStatus, ScanSource
│   ├── connection.py        # Engine + SessionLocal + init_db()
│   └── seed.py              # Demo data (8 pens, 62 pigs, health/farrowing/scan records)
│
├── schemas/                 # Pydantic schemas (pig, pen, health, farrowing, scan)
├── services/                # Business logic (pig, pen, health, farrowing, scan, dashboard)
├── routers/                 # FastAPI routers — kept for Phase 2 commercial use
├── scanner/ocr.py           # Tesseract OCR wrapper
│
├── dashboard/
│   ├── app.py               # Streamlit entry point — injects secrets before DB import
│   ├── api_client.py        # Calls services directly (no HTTP) — same interface as before
│   └── pages/               # dashboard, herd, scan, pens, health, farrowings
│
└── tests/                   # 45 tests, all passing
```

---

## Architecture (Phase 1 — current)

```
Browser → Streamlit dashboard → services → SQLAlchemy → Neon PostgreSQL
```

FastAPI routers still exist in the codebase but are NOT used by the dashboard.
They are kept for **Phase 2 commercial** use (multi-tenant API).

---

## Database

**Local dev:** SQLite (`farmatrack.db`) — auto-created on first run  
**Production:** Neon PostgreSQL (free tier)

### Models
- **Pen** — livestock pen (name, capacity, pen_type)
- **Pig** — individual animal (ear_tag unique, category, breed, weight_kg, pen_id FK, is_active)
- **HealthRecord** — vet records (status, diagnosis, treatment, vet_name, next_checkup)
- **Farrowing** — birth events (live_born, stillborn, mummified, weaned_count) — sow/gilt only
- **ScanLog** — every scan attempt (raw_text, parsed_tag, confidence, source)

### Enums
- `PigCategory`: piglet | finisher | gilt | sow
- `HealthStatus`: healthy | sick | treated | quarantined
- `ScanSource`: ear_tag | manual

### Key rules
- `DELETE /pigs/{id}` is **soft delete** (sets is_active=False, keeps history)
- Farrowings only allowed for `category = sow` or `gilt`
- ear_tag is globally unique
- ScanLog.pig_id is nullable (unmatched scans still logged)

---

## Deployment

**GitHub:** https://github.com/BorisaAlargic-cyber/farmatrack  
**Streamlit Cloud:** https://share.streamlit.io (deployed from main branch, entry: dashboard/app.py)  
**Database:** Neon PostgreSQL (free tier, eu-west / us-east-1)

### Streamlit Cloud secrets (set in App Settings → Secrets)
```toml
DATABASE_URL = "postgresql://neondb_owner:npg_53EqSLTFfWzc@ep-red-resonance-ap6ltb6v.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
TESSERACT_CMD = "/usr/bin/tesseract"
```

### How secrets work
`dashboard/app.py` explicitly copies `st.secrets` into `os.environ` BEFORE importing
any database modules. This ensures pydantic-settings picks up DATABASE_URL correctly.
The `get_settings()` lru_cache is cleared first to force a fresh read.

### Connection config
- SQLite: uses `check_same_thread=False`
- PostgreSQL: uses `NullPool` (lets Neon/pgBouncer handle pooling) + `sslmode=require`

---

## Git workflow

Every change gets committed with a descriptive message and pushed to GitHub.
Streamlit Cloud auto-redeploys on push to `main`.

### Tags so far
- `v0.1.0` — initial release (all features, 45 tests)
- `v0.2.0` — Streamlit Cloud ready (direct DB client, PostgreSQL support)

### Commit after every change
```bash
git add <files>
git commit -m "feat/fix/improve: description"
git push
# For significant releases:
git tag -a v0.X.0 -m "description" && git push origin v0.X.0
```

---

## What was built (session summary)

1. Full FastAPI backend — pigs, pens, health records, farrowings, scan, dashboard endpoints
2. Streamlit dashboard — 6 pages with full CRUD
3. OCR ear-tag scanner — Tesseract + two-pass tag parser (handles O→0 OCR errors)
4. Live camera scan — `st.camera_input()` on the Scan page (scans automatically on photo)
5. Database seed script — 62 pigs, 8 pens, health/farrowing/scan demo data
6. 45 tests — all passing
7. GitHub repo — auto-deploys to Streamlit Cloud on push
8. Neon PostgreSQL — persistent free database connected to Streamlit Cloud
9. DBeaver connection — SQLite file at `farmatrack.db` for local inspection

### Temporary debug code to remove
`dashboard/app.py` has a sidebar debug line showing the masked DATABASE_URL.
Remove after confirming Streamlit Cloud deployment works:
```python
# Remove this block from dashboard/app.py once deployment is confirmed:
try:
    import re
    _raw = st.secrets.get("DATABASE_URL") or os.environ.get("DATABASE_URL", "NOT SET")
    _masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", _raw)
    st.sidebar.caption(f"🔌 DB: `{_masked}`")
except Exception:
    pass
```

---

## Next steps (Phase 2 — commercial)

When ready to sell to other farms:
1. **Authentication** — JWT login, one account per farm
2. **Multi-tenancy** — farm_id on every table, data isolation between customers
3. **Billing** — Stripe integration, pricing tiers
4. **Weight history** — WeightRecord table (pig_id, weight_kg, recorded_at)
5. **Pen movement log** — PenTransfer table (pig_id, from_pen, to_pen, moved_at)
6. **Upcoming checkup alerts** — surface HealthRecord.next_checkup overdue entries
7. **CSV/PDF export** — printable records for vets
8. **Custom domain** — farmatrack.com
9. **FastAPI backend** — re-enable routers for mobile app / third-party integrations

---

## Known issues / notes

- Pydantic v2 deprecation warning in `config.py` — already fixed (uses SettingsConfigDict)
- Python version: always use `/opt/homebrew/bin/python3.9` locally
- Tesseract must be installed for OCR image scan (`brew install tesseract`)
- `test_farmatrack.db` is created during tests — it's in .gitignore
- The `{database,schemas,...` directory in project root is a misnamed folder — ignore it
