import os
import json
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'swift.db')
DATA_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'swift-data.json')

def init_db():
    print(f"Initializing database at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create swift_tags table (System data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS swift_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg VARCHAR(10) NOT NULL,
        tag VARCHAR(10) NOT NULL,
        sub VARCHAR(10) NOT NULL DEFAULT '',
        name TEXT NOT NULL,
        name_en TEXT,
        len VARCHAR(50),
        mo CHAR(1) NOT NULL DEFAULT 'o',
        sample TEXT,
        desc TEXT,
        desc_en TEXT,
        rules TEXT,
        rules_en TEXT,
        source VARCHAR(20) DEFAULT 'system',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- COMPOSITE UNIQUE KEY to support same tags in different messages
        CONSTRAINT uq_swift_tags UNIQUE (msg, tag, sub)
    );
    """)
    
    # 2. Create swift_custom_tags table (Manual user data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS swift_custom_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg VARCHAR(10) NOT NULL,
        tag VARCHAR(10) NOT NULL,
        sub VARCHAR(10) NOT NULL DEFAULT '',
        name TEXT NOT NULL,
        name_en TEXT,
        len VARCHAR(50),
        mo CHAR(1) NOT NULL DEFAULT 'o',
        sample TEXT,
        desc TEXT,
        desc_en TEXT,
        rules TEXT,
        rules_en TEXT,
        source VARCHAR(20) DEFAULT 'manual',
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT uq_swift_custom_tags UNIQUE (msg, tag, sub)
    );
    """)
    
    # Create indexes for optimal lookup performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_swift_tags_msg ON swift_tags(msg);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_swift_tags_tag ON swift_tags(tag);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_swift_tags_msg_tag ON swift_tags(msg, tag);")
    
    # 3. Seed data from swift-data.json
    if os.path.exists(DATA_JSON_PATH):
        print(f"Reading seed data from: {DATA_JSON_PATH}")
        with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)
            
        inserted_count = 0
        for item in items:
            # Upsert into swift_tags using sqlite3 ON CONFLICT syntax
            cursor.execute("""
            INSERT INTO swift_tags (
                msg, tag, sub, name, name_en, len, mo, sample, desc, desc_en, rules, rules_en, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(msg, tag, sub) DO UPDATE SET
                name=excluded.name,
                name_en=excluded.name_en,
                len=excluded.len,
                mo=excluded.mo,
                sample=excluded.sample,
                desc=excluded.desc,
                desc_en=excluded.desc_en,
                rules=excluded.rules,
                rules_en=excluded.rules_en;
            """, (
                item.get('msg', '').lower(),
                item.get('tag', '').upper(),
                item.get('sub', ''),
                item.get('name', ''),
                item.get('name_en', ''),
                item.get('len', ''),
                item.get('mo', 'o').lower(),
                item.get('sample', ''),
                item.get('desc', ''),
                item.get('desc_en', ''),
                item.get('rules', ''),
                item.get('rules_en', ''),
                item.get('source', 'system')
            ))
            inserted_count += 1
            
        conn.commit()
        print(f"Successfully loaded and upserted {inserted_count} SWIFT tag definitions.")
    else:
        print(f"Warning: Seed file not found at {DATA_JSON_PATH}")
        
    conn.close()

if __name__ == '__main__':
    init_db()
