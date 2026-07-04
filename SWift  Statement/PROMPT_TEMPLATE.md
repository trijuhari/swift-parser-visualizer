# 📋 Prompt Template: Generate SWIFT Tag JSON

Gunakan prompt berikut untuk men-generate data tag SWIFT dari dokumentasi atau sumber referensi menggunakan AI (ChatGPT, Gemini, Claude, dll).

---

## 🔧 Prompt (Copy-Paste)

```
Kamu adalah seorang ahli SWIFT Messaging. Saya akan memberikan informasi tentang tipe pesan SWIFT (misalnya MT103, MT202, MT700, dll). Tolong buatkan data JSON dengan format berikut untuk setiap tag/field yang ada di pesan tersebut.

Format JSON (array of objects):
[
  {
    "msg": "<tipe_pesan_lowercase>",
    "tag": "<nomor_tag_uppercase>",
    "sub": "",
    "name": "<nama_field_bahasa_indonesia>",
    "name_en": "<nama_field_bahasa_inggris>",
    "len": "<format_panjang>",
    "mo": "<m_atau_o>",
    "sample": "<contoh_nilai>",
    "desc": "<deskripsi_bahasa_indonesia>",
    "desc_en": "<deskripsi_bahasa_inggris>",
    "rules": "<aturan_validasi_bahasa_indonesia>",
    "rules_en": "<aturan_validasi_bahasa_inggris>",
    "source": "manual"
  }
]

Aturan pengisian:
- "msg": huruf kecil, contoh: "mt103", "mt202", "mt700"
- "tag": huruf besar, contoh: "20", "32A", "50K", "71A"
- "sub": kosong ("") untuk tag utama/induk, isi dengan nomor/kode sub-field jika ada (misal "1", "2", "EREF")
- "mo": "m" untuk Mandatory, "o" untuk Optional
- "len": format panjang SWIFT standard, contoh: "16x", "6!n3!a15d", "4!c[/35x]"
- "sample": contoh nilai realistis
- "desc" / "desc_en": deskripsi lengkap fungsi field tersebut
- "rules" / "rules_en": aturan validasi dan batasan field

PENTING UNTUK TAG DENGAN SUB-FIELD:
Jika suatu tag memiliki sub-field (contoh: Tag 13C memiliki sub-field Kode Waktu, Waktu, Tanda Offset, dan Offset UTC):
1. Kamu WAJIB membuat 1 entry induk (parent) terlebih dahulu untuk tag tersebut dengan "sub": "". Baris induk ini berfungsi sebagai kontainer utama di tabel UI.
2. Kemudian buat entry terpisah untuk masing-masing sub-field di bawahnya dengan "sub" diisi angka urut ("1", "2", "3", dst).
3. Jika baris induk ("sub": "") tidak dibuat, tag tersebut tidak akan muncul di daftar tabel utama UI.

Buatkan data JSON lengkap untuk: [NAMA TIPE PESAN, misal: MT103 Customer Credit Transfer]
```

---

## 📝 Contoh Penggunaan

### Input ke AI:
```
Buatkan data JSON lengkap untuk: MT103 Customer Credit Transfer
```

### Output yang Diharapkan:
```json
[
  {
    "msg": "mt103",
    "tag": "20",
    "sub": "",
    "name": "Referensi Pengirim",
    "name_en": "Sender's Reference",
    "len": "16x",
    "mo": "m",
    "sample": "FT2306301234567",
    "desc": "Referensi unik yang ditetapkan oleh pengirim pesan untuk mengidentifikasi transaksi.",
    "desc_en": "Unique reference assigned by the sender to identify the transaction.",
    "rules": "Wajib diisi. Maksimal 16 karakter alfanumerik (SWIFT character set).",
    "rules_en": "Mandatory. Maximum 16 alphanumeric characters (SWIFT character set).",
    "source": "manual"
  },
  {
    "msg": "mt103",
    "tag": "13C",
    "sub": "",
    "name": "Indikasi Waktu",
    "name_en": "Time Indication",
    "len": "/8c/4!n1!x4!n",
    "mo": "o",
    "sample": "/CLSTIME/1230+0700",
    "desc": "Spesifikasi waktu pemrosesan transaksi (Kode Waktu, Waktu, Tanda, Offset).",
    "desc_en": "Time specifications for transaction processing (Time Code, Time, Sign, Offset).",
    "rules": "Opsional (O). Terdiri dari Kode Waktu, Waktu, Tanda Offset, dan Offset UTC.",
    "rules_en": "Optional (O). Consists of Time Code, Time, Sign, and UTC Offset.",
    "source": "manual"
  },
  {
    "msg": "mt103",
    "tag": "13C",
    "sub": "1",
    "name": "Kode Waktu",
    "name_en": "Time Indication Code",
    "len": "8c",
    "mo": "o",
    "sample": "/CLSTIME/",
    "desc": "Kode yang mengidentifikasi jenis indikasi waktu (misalnya CLSTIME, RNCTIME, SNDTIME), diapit garis miring.",
    "desc_en": "Code identifying the type of time indication (e.g. CLSTIME, RNCTIME, SNDTIME), enclosed by slashes.",
    "rules": "Opsional (O). Field lengkap berformat /8c/4!n1!x4!n.",
    "rules_en": "Optional (O). Full field format /8c/4!n1!x4!n.",
    "source": "manual"
  }
]
```

---

## 🚀 Cara Import ke Aplikasi

1. Copy output JSON dari AI
2. Buka aplikasi SWIFT Reporting Tool → Tab **Admin**
3. Login sebagai Owner
4. Klik **📥 Import JSON**
5. Paste JSON ke textarea
6. Klik **Preview** → verifikasi data
7. Klik **Konfirmasi & Impor**

Data akan langsung tersimpan ke database SQLite.
