import sqlite3
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

from config import CHROMA_DIR


DB_FILENAME = os.path.join(CHROMA_DIR, "conversations.sqlite3")


def _get_conn():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILENAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            text TEXT,
            timestamp TEXT,
            FOREIGN KEY(conversation_id) REFERENCES conversations(id)
        )
        """
    )
    conn.commit()
    conn.close()


def create_conversation(title: str = None) -> str:
    conv_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations (id, title, created_at) VALUES (?,?,?)", (conv_id, title, created_at))
    conn.commit()
    conn.close()
    return conv_id


def add_message(conversation_id: str, role: str, text: str, timestamp: str = None) -> int:
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (conversation_id, role, text, timestamp) VALUES (?,?,?,?)",
        (conversation_id, role, text, timestamp)
    )
    msg_id = cur.lastrowid
    conn.commit()
    conn.close()
    return msg_id


def get_conversation(conversation_id: str) -> Dict[str, Any]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM conversations WHERE id = ?", (conversation_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    cur.execute(
        "SELECT role, text, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,)
    )
    messages = [dict(m) for m in cur.fetchall()]
    conn.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "messages": messages,
    }


def list_conversations() -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM conversations ORDER BY created_at DESC")
    rows = cur.fetchall()
    results = []
    for r in rows:
        conv_id = r["id"]
        cur.execute("SELECT role, text, timestamp FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 1", (conv_id,))
        last = cur.fetchone()
        results.append({
            "id": conv_id,
            "title": r["title"],
            "created_at": r["created_at"],
            "last_message": dict(last) if last else None,
        })
    conn.close()
    return results
