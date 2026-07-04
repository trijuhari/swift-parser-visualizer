import json

with open('swift-data.json', 'r') as f:
    data = json.load(f)

translations_name = {
    "Nomor Referensi Transaksi": "Transaction Reference Number",
    "Referensi Terkait": "Related Reference",
    "Identifikasi Rekening": "Account Identification",
    "Nomor Laporan / Nomor Urut": "Statement Number / Sequence Number",
    "Saldo Awal": "Opening Balance",
    "Indikator Kredit/Debit": "Credit/Debit Indicator",
    "Tanggal (entri terakhir)": "Date (last entry)",
    "Mata Uang": "Currency",
    "Jumlah (saldo awal/interim)": "Amount (opening/interim balance)",
    "Baris Transaksi": "Statement Line",
    "Tanggal Valuta": "Value Date",
    "Tanggal Entri": "Entry Date",
    "Indikasi Kredit/Debit": "Credit/Debit Indication",
    "Kode Dana": "Funds Code",
    "Jumlah": "Amount",
    "Jenis Transaksi": "Transaction Type",
    "Referensi pemilik rekening": "Account Owner Reference",
    "Referensi bank": "Bank Reference",
    "Informasi Tambahan": "Additional Information",
    "Informasi untuk Pemilik Rekening": "Information to Account Owner",
    "Saldo Akhir (Dana Terbukukan)": "Closing Balance (Booked Funds)",
    "Tanggal Akhir Pembukuan": "Closing Date",
    "Kode Mata Uang": "Currency Code",
    "Saldo Tersedia Akhir": "Closing Available Balance",
    "Saldo Forward Tersedia": "Forward Available Balance",
    "Indikator Batas Minimum (Floor Limit) — Debit": "Floor Limit Indicator — Debit",
    "Indikator Batas Minimum (Floor Limit) — Kredit": "Floor Limit Indicator — Credit",
    "Indikasi Tanggal/Waktu": "Date/Time Indication",
    "Tanggal": "Date",
    "Waktu": "Time",
    "Indikasi zona waktu": "Timezone Indicator",
    "Jumlah dan total entri debit": "Number and Sum of Debit Entries",
    "Jumlah entri": "Number of Entries",
    "Jumlah dan total entri kredit": "Number and Sum of Credit Entries"
}

def translate_desc(desc):
    if not desc: return ""
    d = desc.lower()
    if "tidak digunakan" in d: return "Not used."
    if "nomor rekening" in d: return "Account number."
    if "kode mata uang iso" in d: return "ISO currency code."
    if "c: kredit, d: debit" in d: return "C: Credit, D: Debit."
    if "rincian transaksi" in d: return "Contains transaction details."
    if "id referensi bank" in d: return "Bank reference ID."
    if "rincian referensi bank" in d: return "Bank reference details."
    if "muncul sebagai baris baru" in d: return "Appears as a new line if present; may contain channel name."
    if "kode transaksi swift" in d: return "Uses Swift Transaction Code (see Appendix)."
    if "default 0" in d: return "Default 0."
    if "mengidentifikasi pesan" in d: return f"Used to uniquely identify the {desc.split('pesan ')[-1].split(' secara')[0]} message."
    if "saldo awal" in d: return "Opening balance. 60F = first opening balance; 60M = intermediate opening balance."
    if "saldo akhir final" in d: return "Final closing balance. 62F = final; 62M = intermediate."
    if "tanggal laporan terakhir" in d: return "For 60F: date of the last statement. For 60M: date of current statement."
    if "format tidak terstruktur" in d: return "Unstructured format containing additional transaction info. (Debit/Credit structure applies)."
    if "format sama dengan tag 86" in d: return "Same format as tag 86 in MT940."
    if "jumlah dan total nilai entri" in d: return "Number and total value of entries."
    if "zona waktu" in d: return "Date, time, and timezone when the statement was generated."
    if "selisih jam" in d: return "Hour offset from UTC."
    if "bernilai 1 pada laporan pertama" in d: return "Statement number followed by sequence number; resets to 1 every January 1st."
    if "nilai minimum transaksi" in d: return "Minimum transaction value to be included in the message."
    if "tanggal saldo" in d: return "Balance date."
    if "tersedia pada akhir periode" in d: return "Available balance at the end of the period."
    if "berbasis swift" in d: return "For Swift-based payments, prefixed with 'S' + message type."
    if "+" in d: return "Value: + or -."
    return desc # fallback

for item in data:
    item['name_en'] = translations_name.get(item['name'], item['name'])
    item['desc_en'] = translate_desc(item['desc'])

with open('swift-data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Translation applied.")
