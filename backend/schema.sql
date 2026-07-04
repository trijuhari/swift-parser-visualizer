-- =============================================================================
-- SWIFT REPORTING TOOL — PostgreSQL Database Schema
-- =============================================================================
-- Description : Master reference for SWIFT MT940/MT942/MT950 field definitions
-- Version     : 1.0
-- Created     : 2026-06-30
-- =============================================================================

-- Enable UUID extension (opsional untuk fase 2)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLE: swift_tags
-- Sumber data resmi dari GS Docs. Diisi via migration script.
-- Read-only dari UI (tidak bisa diedit user biasa).
-- =============================================================================
CREATE TABLE IF NOT EXISTS swift_tags (
    id          SERIAL          PRIMARY KEY,

    msg         VARCHAR(10)     NOT NULL,                   -- 'mt940' | 'mt103' | 'mt101' | dst.
    tag         VARCHAR(10)     NOT NULL,                   -- '20', '60F', '61', '86'
    sub         VARCHAR(10)     NOT NULL DEFAULT '',        -- '' (main) | '1','2'.. | 'EREF','REMI'..

    -- Konten Bilingual
    name        TEXT            NOT NULL,                   -- Nama field (Bahasa Indonesia)
    name_en     TEXT,                                       -- Field name (English)

    -- Spesifikasi teknis
    len         VARCHAR(50),                                -- '16X', 'YYMMDD', '15B', '5N/5N'
    mo          CHAR(1)         NOT NULL DEFAULT 'o'        -- 'm' = Mandatory, 'o' = Optional
                                CHECK (mo IN ('m', 'o')),
    sample      TEXT,                                       -- Contoh nilai

    -- Deskripsi & Aturan
    desc        TEXT,                                       -- Keterangan (ID)
    desc_en     TEXT,                                       -- Description (EN)
    rules       TEXT,                                       -- Aturan format & batasan (ID)
    rules_en    TEXT,                                       -- Format rules & constraints (EN)

    -- Metadata
    source      VARCHAR(20)     NOT NULL DEFAULT 'gs-docs', -- 'gs-docs' | 'swift-std'
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Constraint: satu kombinasi msg+tag+sub tidak boleh duplikat
    CONSTRAINT uq_swift_tags UNIQUE (msg, tag, sub)
);

COMMENT ON TABLE  swift_tags               IS 'Kamus referensi tag SWIFT MT940/MT942/MT950 dari GS Docs';
COMMENT ON COLUMN swift_tags.msg           IS 'Tipe pesan SWIFT: mt940, mt942, mt950';
COMMENT ON COLUMN swift_tags.tag           IS 'Nomor tag SWIFT, mis: 20, 60F, 61, 86';
COMMENT ON COLUMN swift_tags.sub           IS 'Sub-field identifier. Kosong untuk field utama';
COMMENT ON COLUMN swift_tags.mo            IS 'm=Mandatory/Wajib, o=Optional/Opsional';
COMMENT ON COLUMN swift_tags.rules         IS 'Aturan format, batasan nilai, dan catatan implementasi (ID)';
COMMENT ON COLUMN swift_tags.rules_en      IS 'Format rules, value constraints, and implementation notes (EN)';


-- =============================================================================
-- TABLE: swift_custom_tags
-- Data manual yang ditambahkan user dari fitur "+ Tambah Baris".
-- Menggantikan localStorage browser — persisten & multi-user ready.
-- =============================================================================
CREATE TABLE IF NOT EXISTS swift_custom_tags (
    id          SERIAL          PRIMARY KEY,

    msg         VARCHAR(10),                                -- boleh NULL untuk custom tag lintas pesan
    tag         VARCHAR(10)     NOT NULL,
    sub         VARCHAR(10)     NOT NULL DEFAULT '',

    -- Konten
    name        TEXT            NOT NULL,
    name_en     TEXT,
    len         VARCHAR(50),
    mo          CHAR(1)         NOT NULL DEFAULT 'o'
                                CHECK (mo IN ('m', 'o')),
    sample      TEXT,
    desc        TEXT,
    desc_en     TEXT,
    rules       TEXT,
    rules_en    TEXT,

    -- Metadata & Audit
    source      VARCHAR(20)     NOT NULL DEFAULT 'manual',
    created_by  VARCHAR(100),                               -- username (fase 2: auth)
    is_active   BOOLEAN         NOT NULL DEFAULT TRUE,      -- soft delete
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  swift_custom_tags          IS 'Tag SWIFT custom yang ditambahkan secara manual oleh user';
COMMENT ON COLUMN swift_custom_tags.is_active IS 'FALSE = soft deleted, tidak muncul di query';
COMMENT ON COLUMN swift_custom_tags.created_by IS 'Username/identifier user yang menambahkan (untuk fase 2)';


-- =============================================================================
-- TABLE: audit_log  (Fase 2 — opsional, bisa skip dulu)
-- Menyimpan history perubahan untuk keperluan audit trail
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL       PRIMARY KEY,
    table_name  VARCHAR(50)     NOT NULL,                   -- 'swift_custom_tags'
    record_id   INTEGER         NOT NULL,
    action      VARCHAR(10)     NOT NULL                    -- 'INSERT' | 'UPDATE' | 'DELETE'
                                CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data    JSONB,                                      -- snapshot sebelum perubahan
    new_data    JSONB,                                      -- snapshot sesudah perubahan
    changed_by  VARCHAR(100),
    changed_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE audit_log IS 'Audit trail untuk perubahan data custom tags';


-- =============================================================================
-- INDEXES — Optimasi query performa
-- =============================================================================

-- Query filter by msg type (paling sering dipakai)
CREATE INDEX IF NOT EXISTS idx_swift_tags_msg     ON swift_tags(msg);

-- Query by tag number (dipakai parser)
CREATE INDEX IF NOT EXISTS idx_swift_tags_tag     ON swift_tags(tag);

-- Query by mandatory/optional filter
CREATE INDEX IF NOT EXISTS idx_swift_tags_mo      ON swift_tags(mo);

-- Composite index untuk query kombinasi msg + tag (dipakai di detail lookup)
CREATE INDEX IF NOT EXISTS idx_swift_tags_msg_tag ON swift_tags(msg, tag);

-- Full-Text Search index — mendukung fitur search di header
CREATE INDEX IF NOT EXISTS idx_swift_tags_fts     ON swift_tags
    USING GIN (
        to_tsvector('simple',
            coalesce(tag,     '') || ' ' ||
            coalesce(name,    '') || ' ' ||
            coalesce(name_en, '') || ' ' ||
            coalesce(desc,    '') || ' ' ||
            coalesce(desc_en, '')
        )
    );

-- Index untuk custom tags (soft delete aware)
CREATE INDEX IF NOT EXISTS idx_custom_tags_active ON swift_custom_tags(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_custom_tags_tag    ON swift_custom_tags(tag);


-- =============================================================================
-- VIEW: v_all_tags
-- Menggabungkan data resmi + custom tags dalam satu query.
-- Ini yang akan di-query oleh API — frontend tidak perlu tahu sumbernya.
-- =============================================================================
CREATE OR REPLACE VIEW v_all_tags AS
    -- Data resmi GS Docs
    SELECT
        id,
        msg,
        tag,
        sub,
        name,
        name_en,
        len,
        mo,
        sample,
        desc,
        desc_en,
        rules,
        rules_en,
        source,
        created_at
    FROM swift_tags

    UNION ALL

    -- Data custom dari user (offset ID agar tidak tabrakan dengan data resmi)
    SELECT
        id + 100000     AS id,
        msg,
        tag,
        sub,
        name,
        name_en,
        len,
        mo,
        sample,
        desc,
        desc_en,
        rules,
        rules_en,
        source,
        created_at
    FROM swift_custom_tags
    WHERE is_active = TRUE;

COMMENT ON VIEW v_all_tags IS 'Gabungan swift_tags (resmi) + swift_custom_tags (manual) yang aktif';


-- =============================================================================
-- FUNCTION: update_updated_at_column
-- Trigger helper — otomatis update kolom updated_at saat row diubah
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Pasang trigger ke kedua tabel
CREATE OR REPLACE TRIGGER trg_swift_tags_updated_at
    BEFORE UPDATE ON swift_tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE TRIGGER trg_custom_tags_updated_at
    BEFORE UPDATE ON swift_custom_tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- =============================================================================
-- SAMPLE QUERIES (untuk referensi / testing)
-- =============================================================================

-- 1. Ambil semua tag MT940 yang Mandatory
-- SELECT tag, sub, name, len, sample FROM v_all_tags WHERE msg='mt940' AND mo='m' ORDER BY tag, sub;

-- 2. Full-text search kata "saldo"
-- SELECT tag, name, desc FROM swift_tags
-- WHERE to_tsvector('simple', name || ' ' || coalesce(desc,'')) @@ plainto_tsquery('simple', 'saldo');

-- 3. Lookup sub-field untuk parser (tag 60F)
-- SELECT sub, name, name_en FROM swift_tags WHERE tag='60F' AND sub != '' ORDER BY sub;

-- 4. Semua custom tags aktif
-- SELECT * FROM swift_custom_tags WHERE is_active = TRUE ORDER BY created_at DESC;
