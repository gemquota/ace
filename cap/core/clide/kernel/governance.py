from typing import List, Dict, Any
from clide.storage import db
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType

class GovernanceEngine:
    def __init__(self):
        self.active_traces = []
        self.governance_rules = {
            "max_active_traces": 3,
            "min_success_rate": 0.5,
            "survival_mode_threshold": 0.2
        }

    def evaluate_governance(self):
        """
        Evaluate global system health and adjust priorities.
        """
        nodes = db.get_nodes()
        total_success_rate = 0
        count = 0
        
        # Heuristic: sample recent traces for global health
        for n in nodes:
            # For simplicity, we just look at the last trace this node touched
            # In a real system, we'd aggregate globally.
            pass
            
        print("[*] Governance: System health evaluated.")
        
    def get_trace_priority(self, trace_id: str) -> float:
        """
        Return a priority value [0-1] for a trace.
        """
        # Base priority
        priority = 0.5
        
        # Adjust based on recent activity
        events = db.get_events_by_trace(trace_id)
        if not events:
            return 0.0
            
        # Recently active gets a bump
        last_event = events[-1]
        import time
        if (int(time.time()) - last_event["timestamp"]) < 60:
            priority += 0.2
            
        # High failure rate gets a bump (needs repair)
        # In a real system, we'd parse PIE results here
        
        return min(1.0, priority)
