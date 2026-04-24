import sqlite3
import os
import json

CORE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROJECT_ROOT = os.path.dirname(CORE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

DB_PATH = os.path.join(DATA_DIR, "cap_events.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    
    with get_connection() as conn:
        conn.executescript(schema)
        conn.commit()

def commit_trace(trace_id, created_at):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO traces (trace_id, created_at) VALUES (?, ?)", (trace_id, created_at))
        conn.commit()

def commit_event(event_dict):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO events (
                event_id, trace_id, node_id, timestamp, logical_clock, layer, event_type, 
                payload, causal_parent, state_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_dict["event_id"],
            event_dict["trace_id"],
            event_dict["node_id"],
            event_dict["timestamp"],
            event_dict["logical_clock"],
            event_dict["layer"],
            event_dict["event_type"],
            event_dict["payload"],
            event_dict["causal_parent"],
            event_dict["state_hash"]
        ))
        
        if event_dict["causal_parent"]:
            conn.execute("INSERT INTO causal_index (child_event_id, parent_event_id) VALUES (?, ?)", 
                         (event_dict["event_id"], event_dict["causal_parent"]))
        
        # Publish to message bus
        conn.execute("INSERT INTO message_bus (event_id, node_id, timestamp) VALUES (?, ?, ?)",
                     (event_dict["event_id"], event_dict["node_id"], event_dict["timestamp"]))
        
        conn.commit()

def get_event(event_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
        return dict(row) if row else None

def get_events_by_trace(trace_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM events WHERE trace_id = ? ORDER BY logical_clock ASC", (trace_id,)).fetchall()
        return [dict(row) for row in rows]

def get_nodes():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM nodes").fetchall()
        return [dict(row) for row in rows]

def register_node(node_id):
    import time
    with get_connection() as conn:
        conn.execute("INSERT OR REPLACE INTO nodes (node_id, last_seen) VALUES (?, ?)", (node_id, int(time.time())))
        conn.commit()

def set_genesis_hash(genesis_hash: str):
    import time
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO system_identity (id, genesis_hash, created_at) VALUES (1, ?, ?)", (genesis_hash, int(time.time())))
        conn.commit()

def get_genesis_hash():
    with get_connection() as conn:
        try:
            row = conn.execute("SELECT genesis_hash FROM system_identity WHERE id = 1").fetchone()
            return row["genesis_hash"] if row else None
        except sqlite3.OperationalError:
            return None
