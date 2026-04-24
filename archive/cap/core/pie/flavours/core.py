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
        completions = [e for e in self.events if e.event_type.value == "EXEC_COMPLETE"]
        
        failures = []
        for c in completions:
            payload = c.payload if isinstance(c.payload, dict) else json.loads(c.payload)
            if payload.get("exit_code", 0) != 0:
                failures.append(c)

        self.state.execution_summary = {
            "total_commands": len(commands),
            "success_rate": 1.0 - (len(failures) / len(commands)) if commands else 1.0,
            "failure_points": [f.causal_parent for f in failures]
        }
        
        # Heuristic intent mapping
        commands_text = ""
        for e in commands:
            payload = e.payload if isinstance(e.payload, dict) else json.loads(e.payload)
            commands_text += " " + payload.get("command", "")
        
        mapping = {
            "mkdir": "directory setup",
            "touch": "file initialization",
            "echo": "telemetry verification",
            "python3": "script execution",
            "pip": "dependency management",
            "git": "version control"
        }
        
        for keyword, label in mapping.items():
            if keyword in commands_text:
                self.state.intent_hypotheses.append({"label": label, "confidence": 0.8})
        
        if len(failures) > 2:
            self.state.anomaly_flags.append("REPEATED_FAILURE_CLUSTER")
            
        for ev in self.events:
            if ev.event_type.value == "ANOMALY":
                payload = ev.payload if isinstance(ev.payload, dict) else json.loads(ev.payload)
                self.state.anomaly_flags.append(payload.get("type", "UNKNOWN_ANOMALY"))

        return self.state
