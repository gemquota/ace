from typing import Dict, Any, List
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from clide.kernel.replay import clide_rollback

def heal_system(trace_id: str, drift_report: Dict[str, Any]):
    """
    Apply healing strategy based on drift report.
    """
    print(f"[*] HEALING INITIATED for trace {trace_id}")
    
    from clide.storage import db
    events = db.get_events_by_trace(trace_id)
    last_event_id = events[-1]["event_id"] if events else None

    # Emit HEAL_START
    heal_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.CAP,
        event_type=EventType.HEAL_START,
        payload={"drift": drift_report},
        causal_parent=last_event_id
    )
    
    severity = drift_report.get("severity", "LOW")
    subsystem = drift_report.get("subsystem", "UNKNOWN")
    
    action_taken = "NONE"
    
    if severity == "HIGH":
        if subsystem == "APC":
            # Execution failure cluster -> Rollback to last good checkpoint
            print(f"  [!] High severity APC drift. Rolling back.")
            last_event = drift_report.get("last_good_event")
            if last_event:
                cap_rollback(trace_id, last_event)
                action_taken = f"ROLLBACK_TO_{last_event}"
        elif subsystem == "CLIDE":
            # Intent conflict -> Rewrite intent
            print(f"  [!] High severity CLIDE drift. Rewriting intent.")
            syscalls.cap_event_commit(
                trace_id=trace_id,
                layer=Layer.CLIDE,
                event_type=EventType.INTENT_REWRITE,
                payload={"reason": "CONFLICT_DETECTED"},
                causal_parent=heal_id
            )
            action_taken = "INTENT_REWRITE"
            
    # Emit HEAL_COMPLETE
    syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.CAP,
        event_type=EventType.HEAL_COMPLETE,
        payload={"action": action_taken},
        causal_parent=heal_id
    )
    
    return action_taken
