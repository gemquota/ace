from typing import List, Any
import json
from pie.inference import InferenceState

class PieFlavour:
    def __init__(self, events: List[Any], engine: Any):
        self.events = events
        self.engine = engine
        self.state = InferenceState(events[0].trace_id if events else "unknown")

    def analyze(self) -> InferenceState:
        # 1. Analytical Improvement Scoping
        execution_times = {}
        command_history = []
        
        for e in self.events:
            e_type = e.event_type.value if hasattr(e.event_type, 'value') else e.event_type
            payload = e.payload if isinstance(e.payload, dict) else json.loads(e.payload)
            
            if e_type == "EXEC_SPAWN":
                cmd = payload.get("command", "unknown") if isinstance(payload, dict) else "unknown"
                command_history.append((e.event_id, cmd, e.timestamp))
            elif e_type == "EXEC_COMPLETE":
                spawn = next((c for c in command_history if c[0] == e.causal_parent), None)
                if spawn:
                    exec_time = e.timestamp - spawn[2]
                    execution_times[spawn[1]] = exec_time

        # 2. Paradigm Shift Alignment Protocol
        slow_commands = [cmd for cmd, t in execution_times.items() if t > 5.0]
        if slow_commands:
            self.state.anomaly_flags.append("PARADIGM_SHIFT_REQUIRED: SLOW_EXECUTION")
            self.state.diagnostic_report["paradigm_shift"] = {
                "reason": "Analytical scoping detected inefficient execution times.",
                "target_commands": slow_commands,
                "proposed_alignment": "Offload to secondary swarm node or optimize context constraints."
            }

        cmd_names = [c[1] for c in command_history]
        if len(cmd_names) > 3 and len(set(cmd_names[-3:])) == 1:
             self.state.anomaly_flags.append("PARADIGM_SHIFT_REQUIRED: RECURSIVE_LOOP_DETECTED")
             self.state.diagnostic_report["paradigm_shift"] = {
                 "reason": "Agent is stuck in a recursive investigative loop.",
                 "target_commands": [cmd_names[-1]],
                 "proposed_alignment": "Force contextual wipe and re-evaluate intent via PIE Sweeper."
             }

        if "paradigm_shift" in getattr(self.state, "diagnostic_report", {}):
             print(f"[!] INTR0SPECTION PROTOCOL TRIGGERED: {self.state.diagnostic_report['paradigm_shift']['proposed_alignment']}")

        return self.state
