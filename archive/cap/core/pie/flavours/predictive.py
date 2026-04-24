from typing import List, Any
import json
from pie.inference import InferenceState

class PieFlavour:
    def __init__(self, events: List[Any], engine: Any):
        self.events = events
        self.engine = engine
        self.state = InferenceState(events[0].trace_id if events else "unknown")

    def analyze(self) -> InferenceState:
        commands = [e for e in self.events if e.event_type.value == "EXEC_SPAWN"]
        
        if commands:
            last_cmd_event = commands[-1]
            payload = last_cmd_event.payload if isinstance(last_cmd_event.payload, dict) else json.loads(last_cmd_event.payload)
            last_cmd_base = payload.get("command", "").split()[0] if payload.get("command") else "unknown"
            
            # Predict next step based on causal weights
            predictions = []
            for edge, weight in self.engine.causal_weights.items():
                if edge.startswith(f"{last_cmd_base}->"):
                    next_cmd = edge.split("->")[1]
                    predictions.append({"step": next_cmd, "confidence": weight})
            
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
            self.state.predictions = predictions[:3] # Top 3 predictions
            
        return self.state
