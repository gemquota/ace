import time
import os
import json
import sqlite3
from typing import Dict, Any, Optional
try:
    import psutil
except ImportError:
    psutil = None

# Default weights for credit calculation
CPU_WEIGHT = 1.0
TIME_WEIGHT = 0.5
TOKEN_WEIGHT = 0.001

class ComputeCredit:
    """Economic model for agent resource consumption."""
    def __init__(self, agent_id: str, db_path: str = "clide_swarm.db"):
        self.agent_id = agent_id
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "clide_swarm.db")
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_wallets (
                    agent_id TEXT PRIMARY KEY,
                    balance REAL DEFAULT 100.0,
                    last_updated INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    amount REAL,
                    transaction_type TEXT, -- 'SPENT', 'EARNED', 'BAILOUT'
                    reason TEXT,
                    timestamp INTEGER
                )
            """)
            conn.execute("INSERT OR IGNORE INTO agent_wallets (agent_id, balance, last_updated) VALUES (?, 100.0, ?)", 
                         (self.agent_id, int(time.time())))
            conn.commit()

    def get_balance(self) -> float:
        with self._get_conn() as conn:
            row = conn.execute("SELECT balance FROM agent_wallets WHERE agent_id = ?", (self.agent_id,)).fetchone()
            return row["balance"] if row else 0.0

    def calculate_cost(self, cpu_time: float, duration: float, est_tokens: int = 0) -> float:
        """credit_cost = (cpu_weight * cpu_time) + (time_weight * duration) + (token_weight * est_tokens)"""
        return (CPU_WEIGHT * cpu_time) + (TIME_WEIGHT * duration) + (TOKEN_WEIGHT * est_tokens)

    def spend(self, amount: float, reason: str) -> bool:
        with self._get_conn() as conn:
            row = conn.execute("SELECT balance FROM agent_wallets WHERE agent_id = ?", (self.agent_id,)).fetchone()
            if not row or row["balance"] < amount:
                return False
            
            conn.execute("UPDATE agent_wallets SET balance = balance - ?, last_updated = ? WHERE agent_id = ?", 
                         (amount, int(time.time()), self.agent_id))
            conn.execute("INSERT INTO credit_ledger (agent_id, amount, transaction_type, reason, timestamp) VALUES (?, ?, 'SPENT', ?, ?)", 
                         (self.agent_id, amount, reason, int(time.time())))
            conn.commit()
            return True

    def earn(self, amount: float, reason: str):
        with self._get_conn() as conn:
            conn.execute("UPDATE agent_wallets SET balance = balance + ?, last_updated = ? WHERE agent_id = ?", 
                         (amount, int(time.time()), self.agent_id))
            conn.execute("INSERT INTO credit_ledger (agent_id, amount, transaction_type, reason, timestamp) VALUES (?, ?, 'EARNED', ?, ?)", 
                         (self.agent_id, amount, reason, int(time.time())))
            conn.commit()

    def genesis_bailout(self, amount: float = 50.0):
        """Emergency credit injection for bankrupt agents."""
        with self._get_conn() as conn:
            conn.execute("UPDATE agent_wallets SET balance = ?, last_updated = ? WHERE agent_id = ?", 
                         (amount, int(time.time()), self.agent_id))
            conn.execute("INSERT INTO credit_ledger (agent_id, amount, transaction_type, reason, timestamp) VALUES (?, ?, 'BAILOUT', 'GENESIS_BAILOUT', ?)", 
                         (self.agent_id, amount, int(time.time())))
            conn.commit()

def get_process_stats():
    """Helper to get current process CPU consumption."""
    if psutil:
        p = psutil.Process()
        return {
            "cpu_percent": p.cpu_percent(),
            "cpu_time": p.cpu_times().user + p.cpu_times().system
        }
    return {"cpu_percent": 0.0, "cpu_time": 0.0}
