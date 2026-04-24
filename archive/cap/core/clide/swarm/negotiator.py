import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional
from clide.swarm.ledger import SwarmLedger

class NegotiationSession:
    def __init__(self, task_id: str, agents: List[str]):
        self.session_id = str(uuid.uuid4())
        self.task_id = task_id
        self.agents = agents
        self.turns = []
        self.max_turns = 3
        self.status = "ACTIVE" # ACTIVE, RESOLVED, FAILED

    def add_turn(self, agent_id: str, proposal: str, cost: float):
        if len(self.turns) >= self.max_turns:
            self.status = "FAILED"
            return False
        
        self.turns.append({
            "agent_id": agent_id,
            "proposal": proposal,
            "cost": cost,
            "timestamp": int(time.time())
        })
        
        if len(self.turns) >= self.max_turns:
            self.status = "RESOLVED"
        return True

    def get_final_decision(self) -> Optional[str]:
        """Simple resolution: choose the proposal with lowest cost and highest 'confidence' (simulated)."""
        if not self.turns:
            return None
        # Sort by cost (lowest first)
        sorted_proposals = sorted(self.turns, key=lambda x: x["cost"])
        return sorted_proposals[0]["agent_id"]

class SwarmNegotiator:
    def __init__(self):
        self.ledger = SwarmLedger()
        self.active_sessions = {}

    def start_negotiation(self, task_id: str, agent_ids: List[str]) -> str:
        session = NegotiationSession(task_id, agent_ids)
        self.active_sessions[session.session_id] = session
        print(f"[*] NEGOTIATION: Started session {session.session_id[:8]} for task {task_id[:8]}")
        return session.session_id

    def submit_proposal(self, session_id: str, agent_id: str, proposal: str, cost: float):
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        res = session.add_turn(agent_id, proposal, cost)
        
        if session.status == "RESOLVED":
            winner = session.get_final_decision()
            print(f"[*] NEGOTIATION: Session {session_id[:8]} resolved. Winner: {winner}")
            self.ledger.assign_task(session.task_id, winner)
            del self.active_sessions[session_id]
            
        return res
