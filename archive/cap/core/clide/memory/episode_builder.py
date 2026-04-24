import json
from typing import List, Dict, Any, Optional
from clide.memory.episodic_index import Episode
from clide.types.event_types import EventType, Layer

class EpisodeBuilder:
    """
    Constructs an Episode from a trace's raw event stream.
    """
    def __init__(self, trace_id: str):
        self.trace_id = trace_id

    def build_from_raw_events(self, events: List[Dict[str, Any]]) -> Optional[Episode]:
        if not events: return None
        
        # 1. Identify goal (usually first GOAL_GENERATED event)
        goal_event = next((e for e in events if e.get("event_type") == EventType.GOAL_GENERATED.value), None)
        if not goal_event: return None
        payload = json.loads(goal_event["payload"]) if isinstance(goal_event["payload"], str) else goal_event["payload"]
        goal_str = payload.get("goal", "unknown goal")

        # 2. Extract agent IDs
        agents = set()
        for e in events:
             p = json.loads(e["payload"]) if isinstance(e["payload"], str) else e["payload"]
             if p.get("agent_id"): agents.add(p["agent_id"])
             if "agent" in e.get("event_id", ""): # Heuristic
                  agents.add(e.get("event_id").split("_")[-1])

        # 3. Determine outcome (look for failures in EXEC_COMPLETE)
        failures = [e for e in events if e.get("event_type") == EventType.EXEC_COMPLETE.value and json.loads(e["payload"]).get("exit_code") != 0]
        successes = [e for e in events if e.get("event_type") == EventType.EXEC_COMPLETE.value and json.loads(e["payload"]).get("exit_code") == 0]
        
        outcome = "success"
        if failures:
             outcome = "partial" if successes else "failure"

        # 4. Identify key decisions
        decisions = []
        for e in events:
            if e.get("event_type") in [EventType.GOAL_GENERATED.value, EventType.STRATEGY_SWITCH.value, "PLAN_MUTATION"]:
                 decisions.append({
                     "type": e["event_type"],
                     "timestamp": e["timestamp"],
                     "payload": json.loads(e["payload"]) if isinstance(e["payload"], str) else e["payload"]
                 })

        return Episode(
            trace_id=self.trace_id,
            start_time=events[0]["timestamp"],
            end_time=events[-1]["timestamp"],
            goal=goal_str,
            events=[e["event_id"] for e in events],
            outcome=outcome,
            agents_involved=list(agents),
            key_decisions=decisions,
            summary=f"Processed goal: {goal_str}. Outcome: {outcome}."
        )
