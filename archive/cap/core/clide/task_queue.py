import sqlite3
import json
import time
import uuid
from typing import List, Dict, Any, Optional
from clide.storage import db

LEASE_DURATION = 30 # seconds
STALE_THRESHOLD = 60 # seconds

def push_task(trace_id: str, action_node_dict: Dict[str, Any], causal_parent: str = None, priority: float = 5.0):
    task_id = str(uuid.uuid4())
    now = int(time.time())
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO task_queue (task_id, trace_id, causal_parent, action_payload, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, trace_id, causal_parent, json.dumps(action_node_dict), priority, now))
        conn.commit()
    return task_id

def claim_task(node_id: str) -> Optional[Dict[str, Any]]:
    now = int(time.time())
    lease_expiry = now + LEASE_DURATION
    
    with db.get_connection() as conn:
        # Atomic claim: pick the oldest pending task with highest priority
        row = conn.execute("""
            SELECT task_id, trace_id, causal_parent, action_payload FROM task_queue
            WHERE status = 'PENDING'
            ORDER BY priority DESC, created_at ASC
            LIMIT 1
        """).fetchone()
        
        if row:
            task_id = row['task_id']
            # Attempt to update it atomically
            cursor = conn.execute("""
                UPDATE task_queue SET status = 'CLAIMED', node_id = ?, lease_expiry = ?
                WHERE task_id = ? AND status = 'PENDING'
            """, (node_id, lease_expiry, task_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {
                    "task_id": task_id,
                    "trace_id": row['trace_id'],
                    "causal_parent": row['causal_parent'],
                    "action_payload": json.loads(row['action_payload'])
                }
    return None

def complete_task(task_id: str, success: bool = True):
    now = int(time.time())
    status = "SUCCESS" if success else "FAILED"
    with db.get_connection() as conn:
        conn.execute("""
            UPDATE task_queue SET status = ?, completed_at = ?
            WHERE task_id = ?
        """, (status, now, task_id))
        conn.commit()

def worker_heartbeat(node_id: str, active_tasks: int = 0):
    now = int(time.time())
    with db.get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO nodes (node_id, last_seen, active_tasks)
            VALUES (?, ?, ?)
        """, (node_id, now, active_tasks))
        conn.commit()

def requeue_stale_tasks():
    now = int(time.time())
    with db.get_connection() as conn:
        # Find CLAIMED tasks with expired leases
        cursor = conn.execute("""
            UPDATE task_queue SET status = 'PENDING', node_id = NULL, lease_expiry = NULL
            WHERE status = 'CLAIMED' AND lease_expiry < ?
        """, (now,))
        if cursor.rowcount > 0:
            print(f"[*] Re-queued {cursor.rowcount} stale tasks.")
        conn.commit()

def get_queue_status():
    with db.get_connection() as conn:
        rows = conn.execute("""
            SELECT status, count(*) as count FROM task_queue GROUP BY status
        """).fetchall()
        return {r['status']: r['count'] for r in rows}

def get_active_workers():
    now = int(time.time())
    with db.get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM nodes WHERE last_seen > ?
        """, (now - STALE_THRESHOLD,)).fetchall()
        return [dict(r) for r in rows]
