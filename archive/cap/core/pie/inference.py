from typing import List, Dict, Any, Optional
import os
import json
from clide.memory.retrieval import HybridRetriever
from clide.state_graph import CognitiveStateGraph, NodeType

class InferenceState:
    def __init__(self, trace_id: str, state_graph: Optional[CognitiveStateGraph] = None):
        self.trace_id = trace_id
        self.state_graph = state_graph
        self.intent_hypotheses = []
        self.anomaly_flags = []
        self.execution_summary = {}
        self.predictions = []
        self.causal_weights = {}
        self.diagnostic_report = {}

    def merge(self, other: 'InferenceState'):
        # ... (unchanged)
        if other.intent_hypotheses:
            self.intent_hypotheses.extend(other.intent_hypotheses)
        if other.anomaly_flags:
            self.anomaly_flags.extend(other.anomaly_flags)
        if other.execution_summary:
            self.execution_summary.update(other.execution_summary)
        if other.predictions:
            self.predictions.extend(other.predictions)
        if other.causal_weights:
            self.causal_weights.update(other.causal_weights)
        if other.diagnostic_report:
            self.diagnostic_report.update(other.diagnostic_report)

class PieModelEngine:
# ... (rest of class unchanged)
    def __init__(self, db_path="pie_model.json"):
        self.db_path = db_path
        self.causal_weights = {} # A -> B transition frequency
        self.pattern_memory = {} # Command success/failure stats
        self.temporal_patterns = {} # A -> B success correlation
        self.load_model()

    def load_model(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    self.causal_weights = data.get("causal_weights", {})
                    self.pattern_memory = data.get("pattern_memory", {})
                    self.temporal_patterns = data.get("temporal_patterns", {})
            except:
                pass

    def save_model(self):
        with open(self.db_path, "w") as f:
            json.dump({
                "causal_weights": self.causal_weights,
                "pattern_memory": self.pattern_memory,
                "temporal_patterns": self.temporal_patterns
            }, f, indent=2)

    def evolve(self, events):
        # Update weights and patterns based on trace events
        commands = [] # List of (cmd_base, success)
        
        # Build local execution sequence
        spawn_map = {} # spawn_id -> cmd_base
        for e in events:
            # Handle both Event objects and dicts
            e_type = e.event_type.value if hasattr(e.event_type, 'value') else e.event_type
            payload = e.payload if isinstance(e.payload, dict) else json.loads(e.payload)
            
            if e_type == "EXEC_SPAWN":
                cmd_base = payload["command"].split()[0] if payload["command"] else "unknown"
                spawn_map[e.event_id] = cmd_base
            elif e_type == "EXEC_COMPLETE":
                cmd_base = spawn_map.get(e.causal_parent, "unknown")
                success = payload.get("exit_code") == 0
                commands.append((cmd_base, success))

                # Update pattern memory
                if cmd_base not in self.pattern_memory:
                    self.pattern_memory[cmd_base] = {"success": 0, "failure": 0}
                if success:
                    self.pattern_memory[cmd_base]["success"] += 1
                else:
                    self.pattern_memory[cmd_base]["failure"] += 1
        
        # Update causal transitions
        for i in range(len(commands)-1):
            a_cmd, a_success = commands[i]
            b_cmd, b_success = commands[i+1]
            transition = f"{a_cmd}->{b_cmd}"
            
            # Phase 20: Efficiency Weighting
            # We assume events have credit metadata in a real system
            # For now, we'll boost if success and penalize if failure
            efficiency_multiplier = 1.0
            if a_success and b_success:
                efficiency_multiplier = 1.2 # Economic Boost
            elif not a_success:
                efficiency_multiplier = 0.5 # Economic Penalty
            
            # Frequency with efficiency weighting
            self.causal_weights[transition] = self.causal_weights.get(transition, 0.0) + (1.0 * efficiency_multiplier)
            
            # Temporal Success Correlation
            if transition not in self.temporal_patterns:
                self.temporal_patterns[transition] = {"count": 0, "success_both": 0}
            self.temporal_patterns[transition]["count"] += 1
            if a_success and b_success:
                self.temporal_patterns[transition]["success_both"] += 1
            
        self.save_model()

    def predict(self, last_command: str) -> List[Dict[str, Any]]:
        predictions = []
        for transition, weight in self.causal_weights.items():
            if transition.startswith(f"{last_command}->"):
                next_cmd = transition.split("->")[1]
                # Calculate confidence based on temporal pattern success rate
                pattern = self.temporal_patterns.get(transition, {"count": 1, "success_both": 0})
                confidence = pattern["success_both"] / pattern["count"] if pattern["count"] > 0 else 0
                predictions.append({
                    "next_command": next_cmd,
                    "confidence": round(confidence, 2),
                    "frequency": weight
                })
        return sorted(predictions, key=lambda x: x["frequency"], reverse=True)

def run_flavour(flavour_name: str, events: List[Any], engine: PieModelEngine) -> InferenceState:
    import importlib
    try:
        module = importlib.import_module(f"pie.flavours.{flavour_name}")
        flavour_class = getattr(module, "PieFlavour")
        flavour = flavour_class(events, engine)
        return flavour.analyze()
    except Exception as e:
        print(f"[!] Flavour {flavour_name} failed: {e}")
        state = InferenceState(events[0].trace_id if events else "unknown")
        state.anomaly_flags.append(f"FLAVOUR_{flavour_name.upper()}_ERROR")
        return state

class PieInference:
    def __init__(self, events: List[Any], engine: PieModelEngine = None, state_graph: Optional[CognitiveStateGraph] = None):
        self.events = events
        self.state_graph = state_graph
        self.state = InferenceState(events[0].trace_id if events else "unknown", state_graph=state_graph)
        self.engine = engine or PieModelEngine()
        self.retriever = HybridRetriever()

    def analyze(self, active_flavours=["core", "diagnostic", "predictive", "causal", "neural_alignment"]) -> InferenceState:
        print(f"[*] PIE: Analyzing trace {self.state.trace_id} with flavours {active_flavours}...")
        
        # Phase 20: Context-Augmented Analysis
        if self.state_graph:
            # We can use the graph to find active hypotheses or facts
            active_hypotheses = self.state_graph.get_nodes_by_type(NodeType.HYPOTHESIS)
            if active_hypotheses:
                 print(f"[*] PIE: Found {len(active_hypotheses)} active hypotheses in state graph.")

        for fname in active_flavours:
            print(f"[*] PIE: Running flavour {fname}...")
            partial_state = run_flavour(fname, self.events, self.engine)
            self.state.merge(partial_state)
            
        # 1. Prediction & Deviation Detection
        if self.events:
            print(f"[*] PIE: Processing {len(self.events)} events for predictions...")
            last_exec = next((e for e in reversed(self.events) if (e.event_type.value if hasattr(e.event_type, 'value') else e.event_type) == "EXEC_SPAWN"), None)
            if last_exec:
                payload = last_exec.payload if isinstance(last_exec.payload, dict) else json.loads(last_exec.payload)
                cmd_base = payload["command"].split()[0] if payload["command"] else "unknown"
                self.state.predictions = self.engine.predict(cmd_base)
        
        # 2. Pattern-based Anomaly Detection
        # Detect repeated failures for same command
        fail_counts = {}
        for e in self.events:
            e_type = e.event_type.value if hasattr(e.event_type, 'value') else e.event_type
            if e_type == "EXEC_COMPLETE":
                payload = e.payload if isinstance(e.payload, dict) else json.loads(e.payload)
                if payload.get("exit_code") != 0:
                    # Find command base (simplified)
                    cmd_base = "unknown"
                    fail_counts[cmd_base] = fail_counts.get(cmd_base, 0) + 1
                    if fail_counts[cmd_base] > 2:
                        self.state.anomaly_flags.append(f"REPEATED_FAILURE:{cmd_base}")

        # Phase 16: Check for historical anomalies
        failures = [e for e in self.events if (e.event_type.value if hasattr(e.event_type, 'value') else e.event_type) == "EXEC_COMPLETE" and (e.payload if isinstance(e.payload, dict) else json.loads(e.payload)).get("exit_code") != 0]
        if failures:
            print(f"[*] PIE: Found {len(failures)} failures, checking historical anomalies...")
            intent_event = next((e for e in self.events if (e.event_type.value if hasattr(e.event_type, 'value') else e.event_type) == "INTENT_CREATE"), None)
            if intent_event:
                payload = intent_event.payload if isinstance(intent_event.payload, dict) else json.loads(intent_event.payload)
                intent_label = payload.get("metadata", {}).get("primitive", "default")
                hist_failures = self.retriever.get_relevant_failures(intent_label)
                if hist_failures:
                    self.state.anomaly_flags.append(f"HISTORICAL_FAILURE_MATCH:{intent_label}")

        # 3. Model Evolution Loop
        print(f"[*] PIE: Evolving model...")
        self.engine.evolve(self.events)
        self.state.causal_weights = self.engine.causal_weights
        
        print(f"[*] PIE: Analysis complete for trace {self.state.trace_id}. Diagnostic Report keys: {self.state.diagnostic_report.keys()}")
        return self.state
