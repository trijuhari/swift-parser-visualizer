import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes to support requests from the frontend
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'swift.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/tags', methods=['GET'])
def get_tags():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Combine system tags and custom tags in a single union query, including is_active status
        query = """
        SELECT id, msg, tag, sub, name, name_en, len, mo, sample, desc, desc_en, rules, rules_en, source, 1 AS is_active, created_at
        FROM swift_tags
        UNION ALL
        SELECT id + 100000 AS id, msg, tag, sub, name, name_en, len, mo, sample, desc, desc_en, rules, rules_en, source, is_active, created_at
        FROM swift_custom_tags
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert sqlite3.Row items to dictionary list
        data = [dict(row) for row in rows]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags', methods=['POST'])
def save_tag():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Missing request body"}), 400
            
        msg = (data.get('msg') or '').lower().strip()
        tag = (data.get('tag') or '').upper().strip()
        sub = (data.get('sub') or '').strip()
        
        if not msg or not tag:
            return jsonify({"error": "msg and tag are required fields"}), 400
            
        name = (data.get('name') or '').strip()
        name_en = (data.get('name_en') or '').strip()
        length = (data.get('len') or '').strip()
        mo = (data.get('mo') or 'o').lower().strip()
        sample = (data.get('sample') or '').strip()
        desc = (data.get('desc') or '').strip()
        desc_en = (data.get('desc_en') or '').strip()
        rules = (data.get('rules') or '').strip()
        rules_en = (data.get('rules_en') or '').strip()
        source = (data.get('source') or 'manual').strip()
        is_active = data.get('is_active', 1)
        if isinstance(is_active, bool):
            is_active = 1 if is_active else 0
        else:
            try:
                is_active = int(is_active)
            except:
                is_active = 1

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tag exists in swift_tags (system table)
        cursor.execute(
            "SELECT id FROM swift_tags WHERE LOWER(msg)=? AND UPPER(tag)=? AND sub=?",
            (msg.lower(), tag.upper(), sub)
        )
        system_row = cursor.fetchone()
        
        if system_row:
            # Update existing system tag in-place
            cursor.execute("""
            UPDATE swift_tags SET
                name=?, name_en=?, len=?, mo=?, sample=?, desc=?, desc_en=?, rules=?, rules_en=?
            WHERE LOWER(msg)=? AND UPPER(tag)=? AND sub=?
            """, (name, name_en, length, mo, sample, desc, desc_en, rules, rules_en,
                  msg.lower(), tag.upper(), sub))
        else:
            # Upsert in swift_custom_tags
            cursor.execute("""
            INSERT INTO swift_custom_tags (
                msg, tag, sub, name, name_en, len, mo, sample, desc, desc_en, rules, rules_en, source, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(msg, tag, sub) DO UPDATE SET
                name=excluded.name,
                name_en=excluded.name_en,
                len=excluded.len,
                mo=excluded.mo,
                sample=excluded.sample,
                desc=excluded.desc,
                desc_en=excluded.desc_en,
                rules=excluded.rules,
                rules_en=excluded.rules_en,
                is_active=excluded.is_active,
                updated_at=CURRENT_TIMESTAMP;
            """, (msg, tag, sub, name, name_en, length, mo, sample, desc, desc_en, rules, rules_en, source, is_active))
        
        conn.commit()
        conn.close()
        return jsonify({"message": "Tag saved successfully", "status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags/import', methods=['POST'])
def import_tags():
    try:
        items = request.json
        if not items or not isinstance(items, list):
            return jsonify({"error": "Request body must be a non-empty array"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        imported_count = 0
        for item in items:
            msg = (item.get('msg') or '').lower().strip()
            tag = (item.get('tag') or '').upper().strip()
            sub = (item.get('sub') or '').strip()
            
            if not msg or not tag:
                continue
                
            name = (item.get('name') or '').strip()
            name_en = (item.get('name_en') or '').strip()
            length = (item.get('len') or '').strip()
            mo = (item.get('mo') or 'o').lower().strip()
            sample = (item.get('sample') or '').strip()
            desc = (item.get('desc') or '').strip()
            desc_en = (item.get('desc_en') or '').strip()
            rules = (item.get('rules') or '').strip()
            rules_en = (item.get('rules_en') or '').strip()
            source = (item.get('source') or 'manual').strip()

            # Check if tag exists in swift_tags (system table)
            cursor.execute(
                "SELECT id FROM swift_tags WHERE LOWER(msg)=? AND UPPER(tag)=? AND sub=?",
                (msg.lower(), tag.upper(), sub)
            )
            system_row = cursor.fetchone()
            
            if system_row:
                # Update existing system tag in-place
                cursor.execute("""
                UPDATE swift_tags SET
                    name=?, name_en=?, len=?, mo=?, sample=?, desc=?, desc_en=?, rules=?, rules_en=?
                WHERE LOWER(msg)=? AND UPPER(tag)=? AND sub=?
                """, (name, name_en, length, mo, sample, desc, desc_en, rules, rules_en,
                      msg.lower(), tag.upper(), sub))
            else:
                # Upsert in swift_custom_tags
                cursor.execute("""
                INSERT INTO swift_custom_tags (
                    msg, tag, sub, name, name_en, len, mo, sample, desc, desc_en, rules, rules_en, source, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(msg, tag, sub) DO UPDATE SET
                    name=excluded.name,
                    name_en=excluded.name_en,
                    len=excluded.len,
                    mo=excluded.mo,
                    sample=excluded.sample,
                    desc=excluded.desc,
                    desc_en=excluded.desc_en,
                    rules=excluded.rules,
                    rules_en=excluded.rules_en,
                    is_active=1,
                    updated_at=CURRENT_TIMESTAMP;
                """, (msg, tag, sub, name, name_en, length, mo, sample, desc, desc_en, rules, rules_en, source))
                
            imported_count += 1
            
        conn.commit()
        conn.close()
        return jsonify({"message": f"Successfully imported {imported_count} tags", "count": imported_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags/delete-multiple', methods=['POST', 'OPTIONS'])
def delete_multiple_tags():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
    try:
        data = request.json
        if not isinstance(data, list):
            return jsonify({"error": "Request body must be a list of tags"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        deleted_count = 0
        for item in data:
            msg = (item.get('msg') or '').lower().strip()
            tag = (item.get('tag') or '').upper().strip()
            sub = (item.get('sub') or '').strip()
            
            # Delete from system tags
            cursor.execute("""
            DELETE FROM swift_tags 
            WHERE LOWER(msg) = ? AND UPPER(tag) = ? AND sub = ?
            """, (msg, tag, sub))
            deleted_count += cursor.rowcount
            
            # Also delete from swift_custom_tags
            cursor.execute("""
            DELETE FROM swift_custom_tags 
            WHERE LOWER(msg) = ? AND UPPER(tag) = ? AND sub = ?
            """, (msg, tag, sub))
            deleted_count += cursor.rowcount
            
        conn.commit()
        conn.close()
        
        return jsonify({"message": f"Successfully deleted {deleted_count} records", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tags/<msg>/<tag>', defaults={'sub': ''}, methods=['DELETE', 'OPTIONS'])
@app.route('/api/tags/<msg>/<tag>/', defaults={'sub': ''}, methods=['DELETE', 'OPTIONS'])
@app.route('/api/tags/<msg>/<tag>/<sub>', methods=['DELETE', 'OPTIONS'])
def delete_tag(msg, tag, sub):
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete from swift_tags (system table)
        cursor.execute("""
        DELETE FROM swift_tags 
        WHERE LOWER(msg) = ? AND UPPER(tag) = ? AND sub = ?
        """, (msg.lower(), tag.upper(), sub))
        affected_system = cursor.rowcount
        
        # Also delete/deactivate from swift_custom_tags
        cursor.execute("""
        DELETE FROM swift_custom_tags 
        WHERE LOWER(msg) = ? AND UPPER(tag) = ? AND sub = ?
        """, (msg.lower(), tag.upper(), sub))
        affected_custom = cursor.rowcount
        
        total_affected = affected_system + affected_custom
        conn.commit()
        conn.close()
        
        if total_affected == 0:
            return jsonify({"error": "Tag not found"}), 404
            
        return jsonify({"message": "Tag deleted successfully", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data or 'password' not in data:
            return jsonify({"error": "Password is required"}), 400
            
        # Hardcoded password check matching client-side expectation
        if data['password'] == 'swift2024':
            return jsonify({"status": "success", "token": "swift-owner-authorized-token"}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server on port 8766
    app.run(host='0.0.0.0', port=8766, debug=True)
