import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), "clide_memory.db")

def get_connection():
    conn = sqlite3.connect(MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_memory_db():
    schema = """
    CREATE TABLE IF NOT EXISTS command_sequences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        intent_label TEXT,
        command_sequence TEXT, -- JSON list of commands
        outcome TEXT, -- 'success' or 'failure'
        trace_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        weight REAL DEFAULT 1.0,
        metadata TEXT -- JSON blob for env, etc.
    );

    CREATE TABLE IF NOT EXISTS pattern_weights (
        pattern_hash TEXT PRIMARY KEY,
        pattern_type TEXT, -- 'n-gram', 'dag_fragment'
        weight REAL DEFAULT 1.0,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_intent ON command_sequences(intent_label);
    """
    with get_connection() as conn:
        conn.executescript(schema)
        conn.commit()

class MemoryStore:
    def __init__(self):
        if not os.path.exists(MEMORY_DB_PATH):
            init_memory_db()

    def get_connection(self):
        return get_connection()

    def store_sequence(self, intent_label: str, commands: List[str], outcome: str, trace_id: str, metadata: Dict[str, Any] = None):
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO command_sequences (intent_label, command_sequence, outcome, trace_id, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (intent_label, json.dumps(commands), outcome, trace_id, json.dumps(metadata or {})))
            conn.commit()

    def update_pattern_weight(self, pattern_hash: str, pattern_type: str, delta: float):
        with get_connection() as conn:
            # Check if exists
            row = conn.execute("SELECT weight FROM pattern_weights WHERE pattern_hash = ?", (pattern_hash,)).fetchone()
            if row:
                conn.execute("UPDATE pattern_weights SET weight = weight + ?, last_updated = CURRENT_TIMESTAMP WHERE pattern_hash = ?", (delta, pattern_hash))
            else:
                conn.execute("INSERT INTO pattern_weights (pattern_hash, pattern_type, weight) VALUES (?, ?, ?)", (pattern_hash, pattern_type, 1.0 + delta))
            conn.commit()

    def get_successful_sequences(self, intent_label: str, limit: int = 5) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM command_sequences 
                WHERE intent_label = ? AND outcome = 'success'
                ORDER BY weight DESC, timestamp DESC
                LIMIT ?
            """, (intent_label, limit)).fetchall()
            return [dict(row) for row in rows]

    def prune_stale_patterns(self, weight_threshold: float = 0.1):
        with get_connection() as conn:
            conn.execute("DELETE FROM pattern_weights WHERE weight < ?", (weight_threshold,))
            conn.commit()
