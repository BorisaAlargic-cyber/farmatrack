# FarmaTrack — Diagrams

> **How to view:** Open this file in VS Code with the "Markdown Preview Mermaid Support" extension,
> or paste any diagram block into **https://mermaid.live**

---

## 1. Database ER Diagram

```mermaid
erDiagram
    PEN {
        int     id          PK
        string  name        "unique, e.g. Finishing-1"
        int     capacity    "max pigs"
        string  pen_type    "farrowing | nursery | finishing | quarantine"
        datetime created_at
    }

    PIG {
        int     id           PK
        string  ear_tag      "unique, e.g. SOW-001"
        enum    category     "piglet | finisher | gilt | sow"
        string  breed        "Large White, Landrace, Duroc..."
        date    date_of_birth
        float   weight_kg    "latest weight only (no history yet)"
        int     pen_id       FK
        bool    is_active    "false = soft-deleted"
        text    notes
        datetime created_at
        datetime updated_at
    }

    HEALTH_RECORD {
        int     id           PK
        int     pig_id       FK
        enum    status       "healthy | sick | treated | quarantined"
        string  diagnosis    "e.g. Respiratory infection"
        text    treatment    "e.g. Antibiotics 5d"
        string  vet_name
        date    record_date
        date    next_checkup "nullable — when to check again"
        text    notes
        datetime created_at
    }

    FARROWING {
        int     id              PK
        int     sow_id          FK  "must be category=sow or gilt"
        date    farrowing_date
        int     live_born
        int     stillborn
        int     mummified
        int     weaned_count    "nullable — filled in at weaning"
        date    wean_date       "nullable"
        text    notes
        datetime created_at
    }

    SCAN_LOG {
        int     id          PK
        int     pig_id      FK  "nullable — null if tag not recognised"
        string  raw_text    "raw input from OCR or user"
        string  parsed_tag  "cleaned tag extracted from raw_text"
        enum    source      "ear_tag | manual"
        float   confidence  "0.40 fallback | 0.85 OCR-corrected | 0.90 clean match"
        datetime scanned_at
    }

    PEN          ||--o{ PIG          : "houses (pen_id)"
    PIG          ||--o{ HEALTH_RECORD : "has health records (pig_id)"
    PIG          ||--o{ FARROWING     : "sow / gilt of litter (sow_id)"
    PIG          ||--o{ SCAN_LOG      : "matched by scan (pig_id)"
```

---

## 2. Architecture Diagram

```mermaid
flowchart TB
    User(["👤 Farm Worker\n(browser)"])

    subgraph StreamlitApp ["Streamlit Dashboard  —  port 8501"]
        direction TB
        Nav["Sidebar Navigation"]

        subgraph Pages["Pages"]
            P1["📊 Dashboard\nKPIs + charts"]
            P2["🐖 Herd\nbrowse / add / edit pigs"]
            P3["📷 Scan\ntext or image ear-tag lookup"]
            P4["🏠 Pens\noccupancy + management"]
            P5["💊 Health\nrecords + vet notes"]
            P6["🍼 Farrowings\nbirth + weaning records"]
        end

        subgraph Components["Reusable Components"]
            C1["pig_card\n(pig detail widget)"]
            C2["status_badge\n(colour-coded health icon)"]
        end

        APIClient["api_client.py\nAll HTTP calls go through here\n(requests library)"]
    end

    subgraph FastAPI ["FastAPI Backend  —  port 8000"]
        direction TB

        subgraph Routers["Routers  (HTTP endpoints)"]
            R1["GET POST PATCH DELETE\n/pigs"]
            R2["GET POST PATCH DELETE\n/health"]
            R3["GET POST PATCH\n/farrowings"]
            R4["GET POST PATCH\n/pens"]
            R5["POST /scan\nPOST /scan/image\nGET /scan/logs"]
            R6["GET /dashboard/summary"]
        end

        subgraph Services["Services  (business logic)"]
            S1["pig_service\nfilter, create, update,\nsoft-delete"]
            S2["health_service\nfull CRUD, filter by pig/status"]
            S3["farrowing_service\nvalidates sow/gilt category"]
            S4["pen_service\noccupancy calculation"]
            S5["scan_service\ntag parser + pig lookup"]
        end

        subgraph Scanner["OCR Scanner"]
            OCR["ocr.py\nTesseract wrapper\n(grayscale + sharpen)"]
            Parser["parse_tag()\nregex + OCR correction\nO→0, I→1 in digits only"]
        end
    end

    subgraph DBLayer ["Database Layer"]
        ORM["SQLAlchemy ORM\nmodels: Pen, Pig, HealthRecord\nFarrowing, ScanLog"]
        DB[("farmatrack.db\nSQLite file\n(swap to PostgreSQL\nvia DATABASE_URL in .env)")]
    end

    subgraph Config["Config  (.env)"]
        E1["DATABASE_URL"]
        E2["API_BASE_URL"]
        E3["TESSERACT_CMD"]
        E4["DEBUG"]
    end

    User -->|"opens browser"| StreamlitApp
    Nav --> Pages
    Pages --> APIClient
    APIClient -->|"HTTP REST JSON"| FastAPI

    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S4
    R5 --> S5
    R5 --> OCR
    R6 --> S1
    R6 --> S3

    OCR --> Parser
    Parser --> S5

    S1 & S2 & S3 & S4 & S5 --> ORM
    ORM <--> DB

    Config -.->|"loaded at startup"| FastAPI
    Config -.->|"API_BASE_URL"| APIClient
```

---

## 3. Request Flow — Example: Scanning an Ear Tag from Image

```mermaid
sequenceDiagram
    actor User
    participant Dashboard as Streamlit Dashboard
    participant API as FastAPI /scan/image
    participant OCR as ocr.py (Tesseract)
    participant Parser as parse_tag()
    participant DB as SQLite

    User->>Dashboard: uploads photo of ear tag
    Dashboard->>API: POST /scan/image  (multipart file)
    API->>OCR: save to temp file, run Tesseract PSM-7
    OCR-->>API: raw_text = "FIN-O12"
    API->>Parser: parse_tag("FIN-O12")
    Note over Parser: Pass 1 — regex fails (O not digit)<br/>Pass 2 — fix digits after dash → "FIN-012"
    Parser-->>API: parsed_tag="FIN-012", confidence=0.85
    API->>DB: SELECT * FROM pigs WHERE ear_tag = "FIN-012"
    DB-->>API: Pig record found
    API->>DB: INSERT INTO scan_logs (...)
    API-->>Dashboard: { pig_id, ear_tag, message, confidence }
    Dashboard->>User: shows pig_card with pig details
```

---

## 4. Data Relationships at a Glance

```
PEN
 └── PIGS  (many pigs per pen, one pen per pig)
      ├── HEALTH_RECORDS  (many per pig, hard delete allowed)
      ├── FARROWINGS      (many per sow/gilt, no delete)
      └── SCAN_LOGS       (many per pig, or orphan if tag not found)
```

**Key rules baked into the code:**
- A pig's `ear_tag` must be globally unique
- `DELETE /pigs/{id}` is a **soft delete** — sets `is_active=false`, keeps all history
- A `FARROWING` can only be created for a pig with `category = sow` or `gilt`
- A `HEALTH_RECORD` requires a valid `pig_id` (validated in service layer)
- `SCAN_LOG.pig_id` is **nullable** — unmatched scans are still recorded

**Enums (change these in `database/enums.py`):**
```
PigCategory  →  piglet | finisher | gilt | sow
HealthStatus →  healthy | sick | treated | quarantined
ScanSource   →  ear_tag | manual
```
