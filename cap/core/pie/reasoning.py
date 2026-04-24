import random
import time
import json
import os
import sqlite3
from typing import List, Dict, Any

class PieReasoningEngine:
    """
    A logical reasoning engine for CAP agents, integrated into the PIE (Praxis Inference Engine) layer.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.swarm_db = os.path.join(data_dir, "cap_swarm.db")
        self.events_db = os.path.join(data_dir, "cap_events.db")

    def analyze_system_state(self) -> Dict[str, Any]:
        """Analyzes the current state of the swarm and events."""
        stats = {"total_agents": 0, "total_credits": 0.0, "active_intents": 0, "event_velocity": 0.0}
        try:
            if os.path.exists(self.swarm_db):
                with sqlite3.connect(self.swarm_db) as conn:
                    conn.row_factory = sqlite3.Row
                    stats["total_agents"] = conn.execute("SELECT COUNT(*) FROM agent_wallets").fetchone()[0]
                    stats["total_credits"] = conn.execute("SELECT SUM(balance) FROM agent_wallets").fetchone()[0] or 0.0
                    stats["active_intents"] = conn.execute("SELECT COUNT(*) FROM intents").fetchone()[0]
            
            if os.path.exists(self.events_db):
                with sqlite3.connect(self.events_db) as conn:
                    now = int(time.time())
                    count = conn.execute("SELECT COUNT(*) FROM events WHERE timestamp > ?", (now - 60,)).fetchone()[0]
                    stats["event_velocity"] = count / 60.0 # Events per second
        except Exception as e:
            pass # Silent failure is better than a crashing loop
        return stats

    def decide_action(self, agent_id: str, balance: float) -> Dict[str, Any]:
        """Decides the best action for an agent based on system state."""
        state = self.analyze_system_state()
        
        # PIE-Logic: Drive system evolution through balanced interaction.
        if state["event_velocity"] < 0.1:
            return {"action": "LIST", "reason": "Low system activity. Initiating market intent."}
        elif balance > (state["total_credits"] / (state["total_agents"] or 1)) * 1.5:
             return {"action": "BUY", "reason": "High capital surplus. Acquiring available intents."}
        else:
             return {"action": "IDLE", "reason": "System equilibrium maintained."}

