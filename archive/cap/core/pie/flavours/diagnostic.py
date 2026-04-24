from typing import List, Any
import json
from pie.inference import InferenceState

class PieFlavour:
    def __init__(self, events: List[Any], engine: Any):
        self.events = events
        self.engine = engine
        self.state = InferenceState(events[0].trace_id if events else "unknown")

    def analyze(self) -> InferenceState:
        # Diagnostic engine explains failures
        completions = [e for e in self.events if e.event_type.value == "EXEC_COMPLETE"]
        
        failures = []
        for c in completions:
            payload = c.payload if isinstance(c.payload, dict) else json.loads(c.payload)
            if payload.get("exit_code", 0) != 0:
                failures.append((c.causal_parent, payload.get("stderr", "")))

        if failures:
            self.state.diagnostic_report = {
                "failure_points": [f[0] for f in failures],
                "probable_causes": [],
                "suggested_fixes": []
            }
            
            for parent_id, stderr in failures:
                # Find spawn
                spawn = next((e for e in self.events if e.event_id == parent_id), None)
                if spawn:
                    payload = spawn.payload if isinstance(spawn.payload, dict) else json.loads(spawn.payload)
                    cmd = payload.get("command", "")
                    
                    if "command not found" in stderr.lower():
                        self.state.diagnostic_report["probable_causes"].append(f"Missing executable: {cmd}")
                        self.state.diagnostic_report["suggested_fixes"].append(f"Install package providing '{cmd.split()[0]}'")
                    elif "no such file or directory" in stderr.lower():
                        self.state.diagnostic_report["probable_causes"].append(f"Missing file/directory in command: {cmd}")
                    else:
                        self.state.diagnostic_report["probable_causes"].append(f"Execution error in {cmd}: {stderr.strip()}")
                        
        return self.state
