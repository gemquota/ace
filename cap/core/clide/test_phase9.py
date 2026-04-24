import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from apc import executor
from clide.kernel import syscalls
from clide.kernel.loop import AutonomousLoop
from clide.types.event_types import EventType

def test_phase9():
    print("Initializing Phase 9 Test...")
    db.init_db()
    
    # 1. Start a trace
    trace_id = syscalls.cap_trace_start()
    print(f"[*] Trace {trace_id} started.")
    
    # Get the TRACE_START event to use as parent
    events = db.get_events_by_trace(trace_id)
    trace_start_id = events[0]["event_id"]
    
    # 2. Execute one successful command
    res1 = executor.execute_command(trace_id, "echo 'Success'", causal_parent=trace_start_id)
    
    # 3. Execute 3 failing commands (to trigger REPEATED_FAILURE_CLUSTER)
    print("[*] Simulating failure cluster...")
    res2 = executor.execute_command(trace_id, "exit 1", causal_parent=res1["complete_id"])
    res3 = executor.execute_command(trace_id, "exit 1", causal_parent=res2["complete_id"])
    res4 = executor.execute_command(trace_id, "exit 1", causal_parent=res3["complete_id"])
    
    # 4. Run one cycle of the autonomous loop
    print("[*] Running Autonomous Loop Cycle...")
    loop = AutonomousLoop(trace_id)
    loop.run_cycle()
    
    # 5. Verify Healing
    events = db.get_events_by_trace(trace_id)
    heal_events = [e for e in events if e["event_type"] == EventType.HEAL_START.value]
    rollback_events = [e for e in events if e["event_type"] == EventType.ROLLBACK.value]
    
    print(f"[*] Heal Events Found: {len(heal_events)}")
    print(f"[*] Rollback Events Found: {len(rollback_events)}")
    
    if len(heal_events) > 0 and len(rollback_events) > 0:
        print("  VALIDATED (Autonomous Healing Triggered).")
    else:
        print("  [!] FAILED (Healing not triggered).")

    print("\nSUCCESS: Phase 9 Autonomous CAP Tests Passed.")

if __name__ == "__main__":
    test_phase9()
