# 📊 SWIFT Reporting Tool

Aplikasi web untuk menelusuri, mengelola, dan memvalidasi kamus referensi tag SWIFT (MT940, MT942, MT950, MT103, dan lainnya). Dilengkapi dengan parser pesan SWIFT mentah, admin dashboard untuk CRUD data, serta backend API berbasis Flask + SQLite.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📖 **Kamus Referensi** | Tabel interaktif untuk semua tag SWIFT dengan filter, search, sorting, dan pagination |
| 🔍 **Raw Message Parser** | Parse dan visualisasi pesan SWIFT mentah secara real-time |
| 🛠️ **Admin Dashboard** | Tambah, edit, hapus tag — termasuk tag bawaan sistem |
| 📥 **Bulk Import JSON** | Import data tag secara massal dari output AI/LLM |
| 🌐 **Multi-Bahasa** | Dukungan Bahasa Indonesia dan English |
| 💾 **Database SQLite** | Penyimpanan persisten dengan composite unique key `(msg, tag, sub)` |
| 🔄 **Auto-Fill Pintar** | Saat menambah tag yang sudah ada di pesan lain, field otomatis terisi |
| 📡 **Offline Fallback** | Jika backend mati, otomatis menggunakan data lokal |

---

## 📁 Struktur Proyek

```
SWift Statement/
├── swift-reporting-tabular.html  # Frontend utama (single-page app)
├── swift-data.json               # Seed data tag SWIFT
├── PROMPT_TEMPLATE.md            # Template prompt untuk generate JSON via AI
├── .gitignore
├── README.md
│
├── backend/                      # Backend API
│   ├── app.py                    # Flask REST API server (port 8766)
│   ├── init_db.py                # Script inisialisasi database
│   ├── schema.sql                # Skema DDL database SQLite
│   └── swift.db                  # Database SQLite (auto-generated, gitignored)
│
├── scripts/                      # Script utilitas & scraper
│   ├── build_dictionary.py       # Build kamus dari sumber referensi
│   ├── add_mt564.py              # Generator data MT564
│   ├── scrape_gs_swift.py        # Scraper halaman SWIFT docs
│   ├── scrape_gs_swift2.py       # Scraper v2
│   └── translate.py              # Helper translasi ID ↔ EN
│
└── docs/                         # Dokumentasi referensi (gitignored PDFs)
    ├── _ ISO20022.pdf
    └── MT940_Structured.pdf
```

---

## 🚀 Quick Start

### 1. Inisialisasi Database

```bash
cd backend
python3 init_db.py
```

Ini akan membuat file `swift.db` dan meng-import data dari `swift-data.json`.

### 2. Jalankan Backend API

```bash
python3 backend/app.py
```

Server Flask akan berjalan di `http://localhost:8766`.

### 3. Jalankan Frontend

```bash
python3 -m http.server 8765
```

Buka browser → `http://localhost:8765/swift-reporting-tabular.html`

---

## 🔌 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/api/tags` | Ambil semua tag (system + custom) |
| `POST` | `/api/tags` | Tambah/update satu tag (upsert) |
| `POST` | `/api/tags/import` | Bulk import array of tags |
| `DELETE` | `/api/tags/<msg>/<tag>/<sub>` | Hapus tag berdasarkan composite key |
| `POST` | `/api/login` | Autentikasi owner (password: `swift2024`) |

---

## 📥 Menambah Data Tag Baru

### Cara 1: Manual via Admin Dashboard
1. Login sebagai Owner
2. Buka tab **Admin** → klik **+ Tambah Baris**
3. Ketik jenis pesan (misal `mt103`) — support autocomplete
4. Isi detail tag → **Simpan**

### Cara 2: Bulk Import via JSON
1. Generate data menggunakan prompt di [`PROMPT_TEMPLATE.md`](PROMPT_TEMPLATE.md)
2. Buka tab **Admin** → klik **📥 Import JSON**
3. Paste JSON → Preview → **Konfirmasi & Impor**

### Cara 3: Langsung via API
```bash
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

## 🗄️ Skema Database

Database menggunakan **composite unique key** `(msg, tag, sub)` untuk mencegah duplikasi dan memungkinkan tag yang sama (misal Tag `20`) memiliki definisi berbeda di setiap tipe pesan:

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
│mt940 │ 60F │  2  │    │      │     │     │       │
└─────────────────────────────────────────────────┘
          ↓ UNION ALL ↓
    ┌──────────────────────┐
    │   GET /api/tags      │  ← Frontend reads this
    │   (merged view)      │
    └──────────────────────┘
```

---

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML5 + CSS3 + JavaScript (zero dependencies)
- **Backend**: Python 3.10+ / Flask / flask-cors
- **Database**: SQLite3
- **Styling**: Custom CSS dengan dark mode, glassmorphism, micro-animations

---

## 📄 License

MIT License
