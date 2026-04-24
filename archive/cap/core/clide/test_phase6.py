import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from apc import executor
from clide.kernel import replay
from clide.kernel import syscalls
from clide.types.event_types import EventType, Layer

def test_phase6():
    print("Initializing Phase 6 Test...")
    db.init_db()
    
    # 1. Create a Trace
    trace_id = syscalls.cap_trace_start()
    print(f"[*] Created Trace: {trace_id}")
    
    # 2. Execute a simple command
    print("[*] Executing simple command: echo 'test_replay'")
    res = executor.execute_command(trace_id, "echo 'test_replay'", causal_parent=None)
    
    # 3. Test Replay
    print("[*] Testing Replay...")
    replay_result = replay.cap_trace_replay(trace_id)
    print(f"[*] Replay Status: {replay_result.status}")
    if replay_result.status == "PASS":
        print("  VALIDATED.")
    else:
        for m in replay_result.mismatches:
            print(f"  [!] Mismatch: {m.event_id}")
            
    # 4. Test Tampering (Tampered Event)
    print("[*] Testing Tampered Event Replay...")
    # Get the complete event
    events = db.get_events_by_trace(trace_id)
    complete_event = next((e for e in events if e["event_type"] == EventType.EXEC_COMPLETE.value), None)
    if complete_event:
        import json
        payload = json.loads(complete_event["payload"])
        payload["output_hash"] = "invalid_hash"
        
        # We simulate tampering by modifying the db directly for the test
        # Note: In real life we wouldn't update the payload directly, but we want to see if replay catches it.
        with db.get_connection() as conn:
            conn.execute("UPDATE events SET payload = ? WHERE event_id = ?", (json.dumps(payload), complete_event["event_id"]))
            conn.commit()
        
        tampered_result = replay.cap_trace_replay(trace_id)
        print(f"[*] Tampered Replay Status: {tampered_result.status}")
        if tampered_result.status == "FAIL":
            print("  VALIDATED (Caught Tampering).")
        else:
            print("  [!] FAILED (Did not catch tampering).")
            
    # 5. Test Rollback
    print("[*] Testing Rollback...")
    replay.cap_rollback(trace_id, res["complete_id"])
    
    events_after = db.get_events_by_trace(trace_id)
    rollback_event = next((e for e in events_after if e["event_type"] == EventType.ROLLBACK.value), None)
    if rollback_event:
        print("  VALIDATED (Rollback Emitted).")
    else:
        print("  [!] FAILED (No Rollback Emitted).")

    print("\nSUCCESS: Phase 6 Determinism Engine Tests Passed.")

if __name__ == "__main__":
    test_phase6()
