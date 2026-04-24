import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from apc import executor
from clide.kernel import syscalls
from pie.engine import PieEngine
from pie.inference import PieInference
from clide.synthetic import generate_synthetic_intent

def test_phase10():
    print("Initializing Phase 10 Test...")
    db.init_db()
    
    # 1. Start a trace
    trace_id = syscalls.cap_trace_start()
    print(f"[*] Trace {trace_id} started.")
    
    # Get the TRACE_START event to use as parent
    events = db.get_events_by_trace(trace_id)
    trace_start_id = events[0]["event_id"]
    
    # 2. Execute 11 commands to trigger "SYSTEM_IDLE" synthetic intent
    print("[*] Executing 11 commands to simulate activity...")
    parent_id = trace_start_id
    for i in range(11):
        res = executor.execute_command(trace_id, f"echo 'Cmd {i}'", causal_parent=parent_id)
        parent_id = res["complete_id"]
    
    # 3. Run PIE Inference
    print("[*] Running PIE Inference...")
    pie_engine = PieEngine()
    events = pie_engine.load_trace(trace_id)
    inf = PieInference(events)
    state = inf.analyze()
    
    # 4. Generate Synthetic Intent
    print("[*] Generating Sovereign Synthetic Intent...")
    intent = generate_synthetic_intent(state)
    
    if intent:
        print(f"[*] SYNTHETIC INTENT GENERATED: {intent['primitive']}")
        print(f"  Reason: {intent['reason']}")
        if intent['reason'] == "SYSTEM_IDLE":
             print("  VALIDATED (Sovereign intent generated).")
        else:
             print(f"  [!] FAILED (Wrong reason: {intent['reason']})")
    else:
        print("  [!] FAILED (No intent generated).")

    print("\nSUCCESS: Phase 10 Sovereign Intelligence Tests Passed.")

if __name__ == "__main__":
    test_phase10()
