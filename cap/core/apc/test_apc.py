import sys
import os
import shutil

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from clide.kernel import syscalls
from apc import executor

def test_apc_execution():
    db.init_db()
    trace_id = syscalls.cap_trace_start()
    
    # Get initial event ID
    events = db.get_events_by_trace(trace_id)
    parent_id = events[0]["event_id"]
    
    print("\nTest 1: Basic Command (echo 'hello')")
    res1 = executor.execute_command(trace_id, "echo 'hello'", parent_id)
    print(f"  Result: code={res1['exit_code']}, stdout='{res1['stdout'].strip()}'")
    if res1["stdout"].strip() != "hello":
        print("  FAILED: Output mismatch")
        return False

    print("\nTest 2: Failing Command (invalid_cmd)")
    res2 = executor.execute_command(trace_id, "non_existent_command_12345", res1["complete_id"])
    print(f"  Result: code={res2['exit_code']}, stderr contains error")
    if res2["exit_code"] == 0:
        print("  FAILED: Expected non-zero exit code")
        return False

    print("\nTest 3: Side Effect (touch test_apc_file.txt)")
    test_file = "test_apc_file.txt"
    # Note: with sandboxing, we don't need to cleanup the host, but we check the sandbox
    res3 = executor.execute_command(trace_id, f"touch {test_file}", res2["complete_id"], persist_sandbox=True)
    
    import json
    spawn_ev = db.get_event(res3["spawn_id"])
    payload = json.loads(spawn_ev["payload"])
    sandbox_path = payload["sandbox_path"]
    sandbox_file = os.path.join(sandbox_path, test_file)
    
    print(f"  Result: code={res3['exit_code']}, sandbox={sandbox_path}")
    if not os.path.exists(sandbox_file):
        print("  FAILED: File not created in sandbox")
        shutil.rmtree(sandbox_path)
        return False
    
    # Cleanup sandbox manually since we used persist_sandbox=True
    shutil.rmtree(sandbox_path)
    
    # Verify events in DB
    print("\nVerifying DB Events...")
    final_events = db.get_events_by_trace(trace_id)
    print(f"  Total events: {len(final_events)}")
    # Expected: TRACE_START, 3*(EXEC_SPAWN + EXEC_COMPLETE) = 7 events total
    if len(final_events) != 7:
        print(f"  FAILED: Expected 7 events, got {len(final_events)}")
        return False
        
    for ev in final_events:
        if ev["event_type"] in ["EXEC_SPAWN", "EXEC_COMPLETE"]:
            import json
            payload = json.loads(ev["payload"])
            if ev["event_type"] == "EXEC_COMPLETE":
                print(f"  Event: {ev['event_type']} | SideEffectHash: {payload.get('side_effect_hash', 'MISSING')[:8]}...")
    
    print("\nSUCCESS: Phase 2 APC Test Passed.")
    return True

if __name__ == "__main__":
    if test_apc_execution():
        sys.exit(0)
    else:
        sys.exit(1)
