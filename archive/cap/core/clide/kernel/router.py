import json
import time
from typing import List, Dict, Any, Optional
from clide.storage import db
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType

class TraceRouter:
    """Handles merging of parallel agent traces back to the master timeline."""
    def __init__(self, master_trace_id: str):
        self.master_trace_id = master_trace_id

    def merge_best_trace(self, agent_traces: List[Dict[str, Any]], causal_parent: Optional[str] = None):
        """
        Evaluate multiple agent traces and merge the best one.
        Criteria: Highest success rate, then lowest credit cost.
        """
        if not agent_traces:
            return None

        # Sort by success rate (desc) then credit cost (asc)
        sorted_traces = sorted(agent_traces, key=lambda x: (x["success_rate"], -x["credit_cost"]), reverse=True)
        winner = sorted_traces[0]
        
        print(f"[*] ROUTER: Merging Agent Trace {winner['trace_id']} into Master.")
        
        # Emit MERGE_AGENT event on master timeline
        syscalls.cap_event_commit(
            trace_id=self.master_trace_id,
            layer=Layer.CAP,
            event_type=EventType.MERGE_AGENT,
            payload={
                "winner_trace_id": winner["trace_id"],
                "winner_agent_id": winner["agent_id"],
                "success_rate": winner["success_rate"],
                "credit_cost": winner["credit_cost"],
                "merge_strategy": "BEST_PERFORMANCE"
            },
            causal_parent=causal_parent
        )
        return winner

    def archive_alternates(self, alternates: List[Dict[str, Any]]):
        for alt in alternates:
            # Non-selected traces are just left in DB but marked as shadow in memory
            # We could emit a shadow event if needed
            pass
