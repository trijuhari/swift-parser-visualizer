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
- "sub": kosong ("") untuk tag utama, isi dengan nomor/kode sub-field jika ada (misal "1", "2", "EREF")
- "mo": "m" untuk Mandatory, "o" untuk Optional
- "len": format panjang SWIFT standard, contoh: "16x", "6!n3!a15d", "4!c[/35x]"
- "sample": contoh nilai realistis
- "desc" / "desc_en": deskripsi lengkap fungsi field tersebut
- "rules" / "rules_en": aturan validasi dan batasan field

Jika tag memiliki sub-field (contoh: Tag 60F memiliki sub-field Indikator C/D, Tanggal, Mata Uang, Jumlah), buatkan entry terpisah untuk masing-masing sub-field dengan "sub" diisi angka urut ("1", "2", "3", dst).

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
    "tag": "23B",
    "sub": "",
    "name": "Kode Operasi Bank",
    "name_en": "Bank Operation Code",
    "len": "4!c",
    "mo": "m",
    "sample": "CRED",
    "desc": "Kode yang menunjukkan jenis operasi bank. CRED untuk kredit biasa, SPAY untuk pembayaran khusus.",
    "desc_en": "Code indicating the type of bank operation. CRED for standard credit, SPAY for special payment.",
    "rules": "Wajib diisi. Nilai valid: CRED, CRTS, SPAY, SPRI, SSTD.",
    "rules_en": "Mandatory. Valid values: CRED, CRTS, SPAY, SPRI, SSTD.",
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
