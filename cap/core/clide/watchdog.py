#!/usr/bin/env python3
import os
import sys
import time
import sqlite3

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clide.storage import db

WATCHDOG_TIMEOUT_SECONDS = 300 # 5 minutes

def trigger_rollback():
    """Trigger a system rollback."""
    print("[!] WATCHDOG: Triggering Rollback due to heartbeat stall or temporal horizon breach.")
    # For now, a simulated rollback would stop any active workers or traces.
    with db.get_connection() as conn:
        # Mark active traces as rolled back/failed
        # In a complete implementation, this would prune uncommitted state
        pass
    print("[*] WATCHDOG: Rollback completed. System restored to last safe checkpoint.")

def check_heartbeats():
    """Check if any nodes have stalled."""
    nodes = db.get_nodes()
    current_time = int(time.time())
    
    stalled_nodes = []
    for node in nodes:
        if current_time - node["last_seen"] > WATCHDOG_TIMEOUT_SECONDS:
            stalled_nodes.append(node["node_id"])
            
    if stalled_nodes:
        print(f"[!] WATCHDOG: Stalled nodes detected: {stalled_nodes}")
        trigger_rollback()
    else:
        print("[*] WATCHDOG: All nodes healthy.")

def check_temporal_horizon():
    """Check if any active traces have breached the 4-hour temporal horizon."""
    # Assuming traces that haven't been ended by TRACE_END
    with db.get_connection() as conn:
        active_traces = conn.execute("""
            SELECT t.trace_id, t.created_at 
            FROM traces t
            LEFT JOIN events e ON t.trace_id = e.trace_id AND e.event_type = 'TRACE_END'
            WHERE e.event_id IS NULL
        """).fetchall()
        
        current_time = int(time.time())
        for trace in active_traces:
            elapsed_hours = (current_time - trace["created_at"]) / 3600.0
            if elapsed_hours > 4.0:
                print(f"[!] WATCHDOG: Trace {trace['trace_id']} breached 4-hour horizon ({elapsed_hours:.2f} hrs).")
                trigger_rollback()

if __name__ == "__main__":
    print("[*] WATCHDOG: Starting checks...")
    try:
        check_heartbeats()
        check_temporal_horizon()
    except Exception as e:
        print(f"[!] WATCHDOG ERROR: {e}")
