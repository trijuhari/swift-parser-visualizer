import os
import sqlite3

def init_compliance_db():
    # Base directory is one level up from scripts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'backend', 'swift.db')
    
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create Table
    print("Creating table swift_compliance_rules...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS swift_compliance_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        pattern TEXT NOT NULL,
        reason TEXT NOT NULL,
        reason_en TEXT NOT NULL,
        severity TEXT DEFAULT 'medium',
        score INTEGER DEFAULT 20,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Check if we already have seeds
    cursor.execute("SELECT COUNT(*) FROM swift_compliance_rules")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Table already has {count} rules. Skipping seeding.")
        conn.close()
        return

    # 2. Seed Initial Rules
    seeds = [
        # Sanctions List
        ('sanction', 'Ali Al-Sadr', 'OFAC - Terorisme Internasional', 'OFAC - International Terrorism', 'high', 60),
        ('sanction', 'Mohammad Farhad', 'Daftar Sanksi Terkonsolidasi UE - Pencucian Uang', 'EU Consolidated Sanction List - Money Laundering', 'high', 60),
        ('sanction', 'Saddam Hussein', 'PBB - Senjata Pemusnah Massal', 'UN Consolidated List - Weapons of Mass Destruction', 'high', 60),
        ('sanction', 'Cartel de Sinaloa', 'OFAC - Perdagangan Narkotika', 'OFAC - Narcotics Trafficking', 'high', 60),
        ('sanction', 'Kim Jong-Un', 'PBB - Pendanaan Senjata Nuklir', 'UN Sanctions - WMD Financing', 'high', 60),
        ('sanction', 'Aleksey Shevtsov', 'Sanksi UE - Serangan Siber', 'EU Sanctions - Cyber Warfare Activities', 'high', 60),
        ('sanction', 'Al-Qaeda', 'PBB - Komite Sanksi Al-Qaida', 'UN Al-Qaida Sanctions Committee', 'high', 60),
        ('sanction', 'Hezbollah', 'OFAC - Organisasi Teroris Asing', 'OFAC - Foreign Terrorist Organization', 'high', 60),
        
        # High Risk Countries (FATF)
        ('country', 'IR', 'FATF Daftar Hitam (Iran)', 'FATF Blacklist (Iran)', 'high', 30),
        ('country', 'KP', 'FATF Daftar Hitam (Korea Utara)', 'FATF Blacklist (North Korea)', 'high', 30),
        ('country', 'MM', 'FATF Daftar Abu-Abu (Myanmar)', 'FATF Grey List (Myanmar)', 'high', 30),
        ('country', 'RU', 'Sanksi Geopolitik Komprehensif (Rusia)', 'Comprehensive Geopolitical Sanctions (Russia)', 'high', 30),
        ('country', 'SY', 'FATF Daftar Abu-Abu (Suriah)', 'FATF Grey List (Syria)', 'high', 30),
        ('country', 'YE', 'FATF Daftar Abu-Abu (Yaman)', 'FATF Grey List (Yemen)', 'high', 30),
        ('country', 'IQ', 'Yurisdiksi dengan Pengawasan Diperketat (Irak)', 'Jurisdiction under Enhanced Due Diligence (Iraq)', 'high', 30),
        
        # Dual Use Keywords
        ('keyword_dual_use', 'centrifuge', 'Teknologi Militer/Nuklir (Centrifuge)', 'Military/Nuclear Tech (Centrifuge)', 'medium', 25),
        ('keyword_dual_use', 'uranium', 'Bahan Nuklir Sensitif', 'Sensitive Nuclear Material', 'high', 40),
        ('keyword_dual_use', 'aluminum tubing', 'Komponen Hulu Ledak/Rudal', 'Missile/Centrifuge Component', 'medium', 25),
        ('keyword_dual_use', 'carbon fiber', 'Bahan Berspesifikasi Militer', 'Military-grade Material', 'medium', 25),
        ('keyword_dual_use', 'military-grade', 'Spesifikasi Militer', 'Military-grade Specification', 'medium', 25),
        ('keyword_dual_use', 'drone', 'Teknologi Pesawat Tanpa Awak', 'Unmanned Aerial Vehicle Tech', 'medium', 25),
        
        # AML Keywords
        ('keyword_aml', 'shell corp', 'Indikasi Perusahaan Cangkang', 'Shell Corporation Indicator', 'medium', 20),
        ('keyword_aml', 'unregistered', 'Layanan Tanpa Izin Resmi', 'Unregistered Entity Indicator', 'medium', 20),
        ('keyword_aml', 'cash payout', 'Pencairan Tunai Cepat', 'Immediate Cash Payout Alert', 'medium', 20),
        ('keyword_aml', 'tax haven', 'Wilayah Suaka Pajak', 'Tax Haven Destination', 'medium', 20),
        ('keyword_aml', 'bearer share', 'Pemberian Saham Atas Unjuk', 'Bearer Shares Usage Indicator', 'medium', 20),
        
        # Structuring
        ('structuring', '9000-10000', 'Jumlah transaksi mendekati batas pelaporan wajib USD 10.000', 'Transaction amount sits right below the mandatory reporting threshold of USD 10,000', 'low', 15)
    ]
    
    print(f"Seeding {len(seeds)} default rules...")
    cursor.executemany("""
    INSERT INTO swift_compliance_rules (category, pattern, reason, reason_en, severity, score)
    VALUES (?, ?, ?, ?, ?, ?)
    """, seeds)
    
    conn.commit()
    print("Database seeding completed successfully.")
    conn.close()

if __name__ == "__main__":
    init_compliance_db()
