import sqlite3
import os
import time
import json
from typing import List, Dict, Any, Optional

SWARM_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "clide_swarm.db")

class SwarmLedger:
    def __init__(self):
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(SWARM_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS swarm_tasks (
                    task_id TEXT PRIMARY KEY,
                    trace_id TEXT,
                    primitive TEXT,
                    goal TEXT,
                    required_credits REAL DEFAULT 1.0,
                    priority REAL DEFAULT 0.5,
                    status TEXT DEFAULT 'OPEN', -- OPEN, BIDDING, ASSIGNED, COMPLETED, FAILED
                    winner_agent_id TEXT,
                    created_at INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS swarm_bids (
                    bid_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    agent_id TEXT,
                    proposed_cost REAL,
                    confidence REAL,
                    strategy_summary TEXT,
                    status TEXT DEFAULT 'PENDING', -- PENDING, ACCEPTED, REJECTED
                    timestamp INTEGER,
                    FOREIGN KEY (task_id) REFERENCES swarm_tasks(task_id)
                )
            """)
            conn.commit()

    def create_task(self, task_id: str, trace_id: str, primitive: str, goal: str, credits: float = 1.0, priority: float = 0.5):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO swarm_tasks (task_id, trace_id, primitive, goal, required_credits, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, trace_id, primitive, goal, credits, priority, int(time.time())))
            conn.commit()

    def submit_bid(self, bid_id: str, task_id: str, agent_id: str, cost: float, confidence: float, strategy: str):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO swarm_bids (bid_id, task_id, agent_id, proposed_cost, confidence, strategy_summary, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (bid_id, task_id, agent_id, cost, confidence, strategy, int(time.time())))
            conn.commit()

    def get_open_tasks(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM swarm_tasks WHERE status = 'OPEN'").fetchall()
            return [dict(row) for row in rows]

    def get_bids_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM swarm_bids WHERE task_id = ?", (task_id,)).fetchall()
            return [dict(row) for row in rows]

    def assign_task(self, task_id: str, agent_id: str):
        with self._get_conn() as conn:
            conn.execute("UPDATE swarm_tasks SET status = 'ASSIGNED', winner_agent_id = ? WHERE task_id = ?", (agent_id, task_id))
            conn.execute("UPDATE swarm_bids SET status = 'ACCEPTED' WHERE task_id = ? AND agent_id = ?", (task_id, agent_id))
            conn.execute("UPDATE swarm_bids SET status = 'REJECTED' WHERE task_id = ? AND agent_id != ?", (task_id, agent_id))
            conn.commit()
