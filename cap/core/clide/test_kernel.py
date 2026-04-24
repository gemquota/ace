import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType

def test_minimal_trace():
    print("Initializing CAP DB...")
    db.init_db()
    
    print("Starting TRACE...")
    trace_id = syscalls.cap_trace_start()
    print(f"Trace ID: {trace_id}")
    
    # Get the trace start event to use its ID as parent
    events = db.get_events_by_trace(trace_id)
    parent_id = events[0]["event_id"]
    
    print("Emitting INTENT_CREATE...")
    intent_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.CLIDE,
        event_type=EventType.INTENT_CREATE,
        payload={"goal": "test syscalls"},
        causal_parent=parent_id
    )
    
    print("Emitting EXEC_SPAWN...")
    spawn_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.APC,
        event_type=EventType.EXEC_SPAWN,
        payload={"command": "echo hello"},
        causal_parent=intent_id
    )
    
    print("Emitting EXEC_COMPLETE...")
    complete_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.APC,
        event_type=EventType.EXEC_COMPLETE,
        payload={"stdout": "hello", "exit_code": 0},
        causal_parent=spawn_id
    )
    
    print("Ending TRACE...")
    syscalls.cap_trace_end(trace_id, complete_id)
    
    print("\nVerifying Trace Integrity...")
    final_events = db.get_events_by_trace(trace_id)
    
    for i, ev in enumerate(final_events):
        print(f"Event {i}: {ev['event_type']} (ID: {ev['event_id'][:8]}..., Parent: {str(ev['causal_parent'])[:8] if ev['causal_parent'] else 'None'})")
        
        # Validate each event against its parent
        parent = final_events[i-1] if i > 0 else None
        res = syscalls.cap_validate_event(ev, parent)
        if not res.is_valid:
            print(f"  FAILED VALIDATION: {res.errors}")
            return False
        else:
            print("  VALIDATED.")

    print("\nSUCCESS: Phase 1 Minimal Test Passed.")
    return True

if __name__ == "__main__":
    if test_minimal_trace():
        sys.exit(0)
    else:
        sys.exit(1)
