import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from clide.kernel import syscalls
from apc import executor
from pie.engine import PieEngine
from pie.inference import PieInference, InferenceState

def test_pie_inference():
    db.init_db()
    trace_id = syscalls.cap_trace_start()
    
    # Get initial event ID
    events = db.get_events_by_trace(trace_id)
    parent_id = events[0]["event_id"]
    
    print("\nSimulating Execution Trace...")
    res1 = executor.execute_command(trace_id, "mkdir test_dir_pie", parent_id)
    res2 = executor.execute_command(trace_id, "echo 'hello'", res1["complete_id"])
    res3 = executor.execute_command(trace_id, "ls .", res2["complete_id"])
    
    # Simulate a failure
    res4 = executor.execute_command(trace_id, "cat non_existent_file_pie", res3["complete_id"])
    
    print("\nRunning PIE Inference...")
    engine = PieEngine()
    events = engine.load_trace(trace_id)
    inference = PieInference(events)
    state = inference.analyze()
    
    print(f"  Trace ID: {state.trace_id}")
    print(f"  Summary: {state.execution_summary}")
    print(f"  Inferred Intents: {[i['label'] for i in state.intent_hypotheses]}")
    print(f"  Anomaly Flags: {state.anomaly_flags}")
    
    # Verifications
    if "directory setup" not in [i['label'] for i in state.intent_hypotheses]:
        print("  FAILED: Intent 'directory setup' not inferred")
        return False
        
    if state.execution_summary["total_commands"] != 4:
        print(f"  FAILED: Expected 4 commands, got {state.execution_summary['total_commands']}")
        return False
        
    if state.execution_summary["success_rate"] != 0.75:
        print(f"  FAILED: Expected 0.75 success rate, got {state.execution_summary['success_rate']}")
        return False

    print("\nSUCCESS: Phase 3 PIE Test Passed.")
    return True

if __name__ == "__main__":
    if test_pie_inference():
        sys.exit(0)
    else:
        sys.exit(1)
