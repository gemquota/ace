import os
import json
from pie.inference import PieInference, PieModelEngine
from clide.kernel.events import Event
from clide.types.event_types import Layer, EventType

class MockEvent:
    def __init__(self, event_id, event_type, payload, causal_parent=None):
        self.event_id = event_id
        self.trace_id = "test_trace"
        self.event_type = event_type
        self.payload = payload
        self.causal_parent = causal_parent

def test_phase13_temporal_causal():
    print("Initializing Phase 13 Test...")
    model_path = "test_pie_model.json"
    if os.path.exists(model_path):
        os.remove(model_path)
    
    engine = PieModelEngine(db_path=model_path)
    
    # Trace 1: mkdir -> cd -> git (All Success)
    print("[*] Trace 1: Learning Patterns (mkdir -> cd -> git)")
    events1 = [
        MockEvent("s1", EventType.EXEC_SPAWN, {"command": "mkdir test"}),
        MockEvent("c1", EventType.EXEC_COMPLETE, {"exit_code": 0}, causal_parent="s1"),
        MockEvent("s2", EventType.EXEC_SPAWN, {"command": "cd test"}, causal_parent="c1"),
        MockEvent("c2", EventType.EXEC_COMPLETE, {"exit_code": 0}, causal_parent="s2"),
        MockEvent("s3", EventType.EXEC_SPAWN, {"command": "git init"}, causal_parent="c2"),
        MockEvent("c3", EventType.EXEC_COMPLETE, {"exit_code": 0}, causal_parent="s3"),
    ]
    
    inference1 = PieInference(events1, engine=engine)
    state1 = inference1.analyze(active_flavours=[]) # Skip flavors for pure engine test
    
    print(f"  Causal Weights: {state1.causal_weights}")
    if "mkdir->cd" in state1.causal_weights and "cd->git" in state1.causal_weights:
        print("  SUCCESS: Causal transitions learned.")
    else:
        print("  FAILED: Transitions not learned.")
        return False

    # Trace 2: Another mkdir
    print("\n[*] Trace 2: Verifying Predictions")
    events2 = [
        MockEvent("s4", EventType.EXEC_SPAWN, {"command": "mkdir next_proj"}),
        MockEvent("c4", EventType.EXEC_COMPLETE, {"exit_code": 0}, causal_parent="s4"),
    ]
    
    # Reload engine to ensure persistence
    engine2 = PieModelEngine(db_path=model_path)
    inference2 = PieInference(events2, engine=engine2)
    state2 = inference2.analyze(active_flavours=[])
    
    print(f"  Predictions after 'mkdir': {state2.predictions}")
    pred = next((p for p in state2.predictions if p["next_command"] == "cd"), None)
    if pred and pred["confidence"] == 1.0:
        print("  SUCCESS: High-confidence prediction for 'cd' verified.")
    else:
        print(f"  FAILED: Prediction 'cd' not found or low confidence. {pred}")
        return False

    # Trace 3: Repeated Failure Anomaly
    print("\n[*] Trace 3: Repeated Failure Detection")
    events3 = [
        MockEvent("s5", EventType.EXEC_SPAWN, {"command": "bad_cmd"}),
        MockEvent("c5", EventType.EXEC_COMPLETE, {"exit_code": 1}, causal_parent="s5"),
        MockEvent("s6", EventType.EXEC_SPAWN, {"command": "bad_cmd"}),
        MockEvent("c6", EventType.EXEC_COMPLETE, {"exit_code": 1}, causal_parent="s6"),
        MockEvent("s7", EventType.EXEC_SPAWN, {"command": "bad_cmd"}),
        MockEvent("c7", EventType.EXEC_COMPLETE, {"exit_code": 1}, causal_parent="s7"),
    ]
    
    inference3 = PieInference(events3, engine=engine2)
    state3 = inference3.analyze(active_flavours=[])
    
    print(f"  Anomaly Flags: {state3.anomaly_flags}")
    if any("REPEATED_FAILURE" in flag for flag in state3.anomaly_flags):
        print("  SUCCESS: Repeated failure anomaly detected.")
    else:
        print("  FAILED: Anomaly not detected.")
        return False

    # Cleanup
    if os.path.exists(model_path):
        os.remove(model_path)
    
    print("\nSUCCESS: Phase 13 Advanced PIE Intelligence Verified.")
    return True

if __name__ == "__main__":
    import sys
    if not test_phase13_temporal_causal():
        sys.exit(1)
