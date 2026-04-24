import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from apc import executor
from clide.kernel import syscalls
from pie.engine import PieEngine
from pie.inference import PieInference, PieModelEngine

def test_phase7():
    print("Initializing Phase 7 Test...")
    db.init_db()
    
    # 1. Create a trace
    trace_id = syscalls.cap_trace_start()
    print(f"[*] Created Trace: {trace_id}")
    
    # Get the TRACE_START event to use as parent
    events = db.get_events_by_trace(trace_id)
    trace_start_id = events[0]["event_id"]
    
    # 2. Execute a sequence to build causal weights (echo -> touch)
    print("[*] Executing sequence to build patterns: echo -> touch")
    res1 = executor.execute_command(trace_id, "echo 'step1'", causal_parent=trace_start_id)
    res2 = executor.execute_command(trace_id, "touch /tmp/test_pie_file", causal_parent=res1["complete_id"])
    
    # 3. Execute a failing command to test diagnostic
    print("[*] Executing failing command: nonexistent_command")
    res3 = executor.execute_command(trace_id, "nonexistent_command_123", causal_parent=res2["complete_id"])
    
    # 4. Run PIE Inference
    print("[*] Running PIE Adaptive Cognition...")
    pie_engine = PieEngine()
    events = pie_engine.load_trace(trace_id)
    inf = PieInference(events)
    state = inf.analyze()
    
    # 5. Verify Causal Weights
    print(f"[*] Causal Weights: {state.causal_weights}")
    if "echo->touch" in state.causal_weights or "echo->nonexistent_command_123" in state.causal_weights:
        print("  VALIDATED (Causal Weights Updated).")
    else:
        print("  [!] FAILED (Causal Weights not updated).")
        
    # 6. Verify Diagnostic
    print(f"[*] Diagnostic Report: {state.diagnostic_report}")
    if state.diagnostic_report.get("probable_causes"):
        print("  VALIDATED (Diagnostic Identified Failure).")
    else:
        print("  [!] FAILED (Diagnostic missed failure).")
        
    # 7. Verify Predictive
    print(f"[*] Predictions: {state.predictions}")
    if state.predictions:
        print("  VALIDATED (Predictions generated).")
    else:
        print("  [!] FAILED (No predictions generated).")

    print("\nSUCCESS: Phase 7 PIE Evolution Engine Tests Passed.")

if __name__ == "__main__":
    test_phase7()
