import sqlite3
from datetime import datetime

DB_FILE = "nik_knowledge.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            content TEXT,
            source TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_knowledge(topic, content, source="manual"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO knowledge (topic, content, source, created_at)
        VALUES (?, ?, ?, ?)
    """, (topic, content, source, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def search_knowledge(query, limit=3):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT content FROM knowledge
        WHERE topic LIKE ? OR content LIKE ?
        ORDER BY id DESC
        LIMIT ?
    """, (f"%{query}%", f"%{query}%", limit))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]
