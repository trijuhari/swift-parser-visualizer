# 📊 SWIFT Reporting Tool

A professional web portal for browsing, managing, and validating the SWIFT message tag reference dictionary, with a built-in raw SWIFT message parser & interactive visualizer. Features an admin CMS for CRUD operations, a Flask + SQLite backend API, and full bilingual support (Indonesian / English).

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black)

---

## ✨ Key Features

### 🏠 Home Dashboard
- Interactive card boxes for each available SWIFT message type
- Displays the **6 most commonly used types** by default (MT940, MT942, MT950, MT103, MT101, MT564)
- Each card shows a description, tag count, and quick-access buttons to the **Dictionary** and **Parser**
- Global search to discover all other message types
- Automatic filtering: only displays records with active status (`is_active = 1`)

### 📖 Reference Dictionary
- Interactive table for all SWIFT tags with multi-column search, filtering, and sorting
- Click any tag to view full details including sub-fields, format rules, and samples
- Clickable structure tags for direct navigation to related tag definitions
- Filter by message type, mandatory/optional status, and free-text keywords

### 🔍 Visualizer / Raw SWIFT Parser
The parser supports **9 SWIFT message types** with auto-detection:

| Message Type | Description | Parser |
|------------|-----------|--------|
| **MT940** | Customer Statement Message | ✅ Full parser + dashboard visualization |
| **MT942** | Interim Transaction Report | ✅ Full parser + dashboard visualization |
| **MT950** | Statement Message | ✅ Full parser + dashboard visualization |
| **MT103** | Single Customer Credit Transfer | ✅ Full parser + sender/beneficiary cards |
| **MT101** | Request for Transfer | ✅ Full parser + ordering/beneficiary cards |
| **MT102** | Multiple Customer Funds Transfer | ✅ Full parser + bulk payment overview |
| **MT104** | Direct Debit Message | ✅ Full parser + creditor/debtor cards |
| **MT564** | Corporate Action Notification | ✅ Full parser + corporate action options |
| **MT202** | General Financial Institution Transfer | ✅ Full parser + treasury/interbank settlement cards |

**Advanced parser features:**
- 🗺️ **Interactive Bank Pathway Diagram** — Visualizes the complex flow of funds across intermediate correspondent banks and institutions (MT103, MT202, MT101, MT102, and MT104), allowing operatives to inspect individual entity details (SWIFT tags, accounts, addresses, and transaction roles) in real-time.
- 💡 **Executive Business Insights** — Each parser type displays a dynamic, contextual business explanation (bilingual ID/EN)
- ⚠️ **Format Validation** — Automatic detection of missing mandatory tags in the pasted message
- ⚙️ **Developer Utilities** — View and copy the structured JSON output of the parsed message (for API integration / debugging)
- 📊 **Transaction Detail Viewer** — Click any transaction row to view fully parsed sub-fields (MT940/942/950)
- 💰 **Net Cash Flow Analysis** — Automatic inflow/outflow summary with executive narrative (MT940/942/950)
- 🔒 **One-Click SWIFT Data Anonymizer** — Instant client data masking (names, accounts, amounts) directly in the browser, allowing developers and operators to share or troubleshoot production messages safely without violating banking privacy regulations (GDPR/UU PDP).
- 🛡️ **GuardDog Compliance Engine (AML)** — Automated real-time scanning of ordering party, beneficiary, BICs, and narratives against sanctions lists (OFAC, UN, EU), high-risk FATF countries, dual-use keywords, and structuring patterns (amounts approaching $10,000).
- ⚡ **SWIFT gpi Transaction Tracker** — Visualizes correspondent bank hops, status milestones (ACSC, ACSP, HOLD, RJCT) using UETR (Tag `:121:`), and deducts intermediary bank fees and FX spreads.

### 🛠️ Admin Portal (CMS)
- Accessed via direct URL navigation: `admin.html` (no visible button on the public interface)
- Full CRUD: Create, Read, Update, and Delete SWIFT tags
- **Compliance Rules CMS**: Dedicated interface to manage active compliance and AML screening rules (create, edit, soft-delete)
- Bulk JSON import for mass data ingestion
- System tag deactivation (soft-delete) to hide without permanently removing
- Message type category & metadata management


### 🔄 Reconciliation Simulator
- **Multi-Message Processing**: Supports loading and parsing multiple statement messages and payment messages at once (separated by double newlines or `---`).
- **Tiered Matching Engine**: Client-side stateless algorithm executing:
  1. **Exact Match**: Exact amount + payment reference (`:20:`) found in statement narrative.
  2. **Partial Match**: Exact amount + payment reference not found (needs manual review).
  3. **Amount-only Match**: Reference matched + amount within small tolerance (up to 5% or 50.00 units, accounting for fees/charges).
- **Interactive Dashboard**: Bilingual summary cards, comparison tables, side-by-side details, and executive business insights.
- **Developer Utilities**: Export matched output as structured JSON for easy debugging.

### 🌐 Bilingual Support (ID / EN)
- Full support for Bahasa Indonesia (default) and English
- Real-time language toggle without page reload
- All labels, descriptions, rules, and business insights available in both languages

### 🌙 Dark Mode
- Premium dark mode with smooth transitions
- Supports all components including tables, cards, and parser panels

---

## 📁 Project Structure

```
SWift Statement/
├── index.html                    # Main frontend (Single Page Application)
├── admin.html                    # Admin Portal / CMS (direct URL access only)
├── swift-data.json               # SWIFT tag seed data (offline fallback)
├── swift-reporting-tabular.html  # Legacy version (deprecated)
├── PROMPT_TEMPLATE.md            # AI prompt template for generating tag JSON
├── .gitignore
├── README.md
│
├── backend/                      # Backend API
│   ├── app.py                    # Flask REST API server (port 8766)
│   ├── init_db.py                # Database initialization script
│   ├── schema.sql                # SQLite DDL schema
│   └── swift.db                  # SQLite database (auto-generated, gitignored)
│
└── scripts/                      # Utility scripts & scrapers
    ├── setup_compliance_db.py    # Compliance & AML rules setup script
    ├── build_dictionary.py       # Dictionary builder from reference sources
    ├── add_mt564.py              # MT564 data generator
    ├── scrape_gs_swift.py        # SWIFT docs scraper v1
    ├── scrape_gs_swift2.py       # SWIFT docs scraper v2
    └── translate.py              # ID ↔ EN translation helper
```

---

## 🚀 Quick Start

### 1. Initialize the Database

```bash
cd backend
python3 init_db.py
python3 ../scripts/setup_compliance_db.py
```

### 2. Start Both Backend & Frontend Automatically

To run both servers concurrently with a single command:

```bash
./start.sh
```

Or execute using Python directly:

```bash
python3 start.py
```

Open your browser → **`http://localhost:8765`**

> **💡 Note:** The launcher script hosts the Frontend on `http://localhost:8765` and the Backend API on `http://localhost:8766`. Press `Ctrl+C` to terminate both processes safely.

---

## 🔌 API Endpoints

### SWIFT Tag Dictionary Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tags` | Retrieve all tags (system + custom, merged view) |
| `POST` | `/api/tags` | Create or update a single tag (upsert by composite key) |
| `POST` | `/api/tags/import` | Bulk import an array of tags |
| `DELETE` | `/api/tags/<msg>/<tag>/<sub>` | Delete a custom tag or deactivate a system tag |
| `POST` | `/api/tags/delete-multiple` | Delete/deactivate multiple tags at once |
| `POST` | `/api/login` | Admin portal authentication |

### Compliance/AML Rules Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/compliance/rules` | Retrieve all active AML and sanctions screening rules |
| `POST` | `/api/compliance/rules` | Create or update a compliance screening rule |
| `DELETE` | `/api/compliance/rules/<id>` | Soft-delete/deactivate a compliance screening rule |

### Example Request

```bash
# Add a new tag
curl -X POST http://localhost:8766/api/tags \
  -H "Content-Type: application/json" \
  -d '{
    "msg": "mt103",
    "tag": "20",
    "sub": "",
    "name": "Referensi Pengirim",
    "name_en": "Sender'\''s Reference",
    "len": "16x",
    "mo": "m",
    "sample": "FT2306301234567",
    "desc": "Referensi unik pengirim",
    "desc_en": "Unique sender reference",
    "source": "manual"
  }'
```

---

## 📥 Adding New Tag Data

### Option 1: Manual via Admin Portal
1. Navigate to `admin.html` directly in your browser
2. Click **+ Add Row** → Fill in tag details → **Save**

### Option 2: Bulk Import via JSON
1. Generate data using the prompt template in [`PROMPT_TEMPLATE.md`](PROMPT_TEMPLATE.md)
2. In the Admin Portal → click **📥 Import JSON**
3. Paste JSON → Preview → **Confirm & Import**

### Option 3: Direct REST API
Use `POST /api/tags` or `POST /api/tags/import` (see example above)

---

## 🗄️ Database Schema

### SWIFT Tags Tables
The database uses a **composite unique key** `(msg, tag, sub)` to prevent duplicates. The same tag (e.g. Tag `:20:`) can have different definitions across different message types:

```
┌─────────────────────────────────────────────────┐
│ swift_tags (System)  │  swift_custom_tags (User) │
├─────────────────────────────────────────────────┤
│ msg  │ tag │ sub │    │ msg  │ tag │ sub │       │
│──────│─────│─────│    │──────│─────│─────│       │
│mt940 │ 20  │     │    │mt103 │ 20  │     │       │
│mt940 │ 25  │     │    │mt103 │ 23B │     │       │
│mt940 │ 60F │     │    │mt202 │ 20  │     │       │
│mt940 │ 60F │  1  │    │      │     │     │       │
└─────────────────────────────────────────────────┘
          ↓ UNION ALL ↓
    ┌──────────────────────────┐
    │   GET /api/tags          │  ← Frontend reads merged view
    │   WHERE is_active = 1    │  ← Deactivated items filtered out
    └──────────────────────────┘
```

### Compliance Rules Table (`swift_compliance_rules`)
This table holds the patterns and keywords matched by the GuardDog Compliance Engine during parsing:
* `category`: Rule category (`sanction`, `country`, `keyword_dual_use`, `keyword_aml`, `structuring`)
* `pattern`: The pattern to look for (entity name, country code, amount range)
* `reason`/`reason_en`: Bilingual explanations for flagged violations
* `severity`: Severity level (`low`, `medium`, `high`)
* `score`: Risk points to add (accumulated risk scale up to 100)
* `is_active`: Soft-delete status indicator (`1` = active, `0` = inactive)

---

## 🎯 Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Client)                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │   Home    │  │  Reference   │  │  Parser / Viz.    │  │
│  │ Dashboard │  │ (Dictionary) │  │  (8 MT types)     │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│                        │                                 │
│  ┌─────────────────────┴───────────────────────────────┐ │
│  │           index.html (SPA + i18n + Dark Mode)       │ │
│  └─────────────────────┬───────────────────────────────┘ │
└────────────────────────┼─────────────────────────────────┘
                         │ fetch() / XMLHttpRequest
                         ▼
┌────────────────────────────────────────────────┐
│           Flask API (localhost:8766)            │
│  ┌──────────────────────────────────────────┐  │
│  │  GET /api/tags  │  POST  │  DELETE  │ ... │  │
│  └──────────────────────────────────────────┘  │
│                    │                            │
│            ┌───────┴──────────┐                 │
│            │   SQLite (swift.db)               │
│            │   swift_tags + swift_custom_tags   │
│            └──────────────────┘                 │
└────────────────────────────────────────────────┘

Fallback (offline): index.html ← swift-data.json
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vanilla HTML5 + CSS3 + JavaScript ES6+ (zero dependencies) |
| **Backend** | Python 3.10+ / Flask / flask-cors |
| **Database** | SQLite3 with composite unique constraints |
| **Styling** | Custom CSS — dark mode, glassmorphism, micro-animations |
| **Deployment** | Python HTTP server (dev) / deployable to NGINX / Gunicorn |

---

## 📋 Developer Guide

### Adding a New Parser Type
To add parser support for a new SWIFT message type (e.g. MT202):

1. **Create the parser function**: Add `parseMT202(rawText)` that returns a structured object
2. **Create the render function**: Add `renderMT202Output(statement)` for dashboard visualization
3. **Create the insight function**: Add `getMT202BusinessExplanation(statement)` for business analysis
4. **Register in `parseSwift()`**: Add auto-detection logic and routing to the new parser
5. **Update `isParserSupported()`**: Add `'mt202'` to the `supported` array
6. **Update the dropdown**: Add a new `<option>` to `#parserTypeSelect`
7. **Add sample data**: In `loadSampleData()` add a raw message example

### Adding a New Language
All UI text is defined in the `i18n` object inside `index.html`. Add a new key to both `i18n.id` and `i18n.en` for each new label.

---

## 📄 License

MIT License — Free to use for internal, educational, and commercial purposes.
