import json
import random
import math
from typing import List, Dict, Any, Optional
from pie.inference import InferenceState

class PieFlavour:
    """
    Phase 21: Neural Alignment Flavour.
    Simulates high-dimensional vector alignment for intent prediction.
    """
    def __init__(self, events: List[Any], engine: Any):
        self.events = events
        self.engine = engine
        self.trace_id = events[0].trace_id if events else "unknown"
        self.state = InferenceState(self.trace_id)

    def _simulate_neural_embedding(self, text: str) -> List[float]:
        """Simulates a 16-dimensional embedding vector for a command string."""
        random.seed(text)
        return [random.uniform(-1, 1) for _ in range(16)]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculates simulated cosine similarity between two vectors."""
        dot = sum(a*b for a, b in zip(v1, v2))
        m1 = math.sqrt(sum(a*a for a in v1))
        m2 = math.sqrt(sum(b*b for b in v2))
        return dot / (m1 * m2) if m1 * m2 > 0 else 0

    def analyze(self) -> InferenceState:
        # 1. Intent-to-Action Alignment Check
        intents = [e for e in self.events if (e.event_type.value if hasattr(e.event_type, 'value') else e.event_type) == "INTENT_CREATE"]
        actions = [e for e in self.events if (e.event_type.value if hasattr(e.event_type, 'value') else e.event_type) == "EXEC_SPAWN"]
        
        if intents and actions:
            intent_payload = intents[-1].payload if isinstance(intents[-1].payload, dict) else json.loads(intents[-1].payload)
            goal = intent_payload.get("goal", "unknown")
            intent_vec = self._simulate_neural_embedding(goal)
            
            alignment_scores = []
            for action in actions:
                action_payload = action.payload if isinstance(action.payload, dict) else json.loads(action.payload)
                cmd = action_payload.get("command", "unknown")
                action_vec = self._simulate_neural_embedding(cmd)
                score = self._cosine_similarity(intent_vec, action_vec)
                alignment_scores.append(score)
            
            avg_alignment = sum(alignment_scores) / len(alignment_scores)
            self.state.diagnostic_report["neural_alignment_score"] = round(avg_alignment, 3)
            
            # Detect Alignment Drift (Intent vs. Reality)
            if avg_alignment < 0.3:
                self.state.anomaly_flags.append("NEURAL_ALIGNMENT_DRIFT")
                print(f"[!] PIE: NEURAL_ALIGNMENT_DRIFT detected for goal: '{goal[:30]}...' (Score: {avg_alignment:.3f})")

        # 2. Predictive Weight Reinforcement
        # If the last action aligns with historical success, boost its neural weight
        if actions:
            last_action_payload = actions[-1].payload if isinstance(actions[-1].payload, dict) else json.loads(actions[-1].payload)
            last_cmd = last_action_payload.get("command", "").split()[0] if last_action_payload.get("command") else "unknown"
            
            # Simulated 'Neural' confidence based on historical pattern success
            pattern_stat = self.engine.pattern_memory.get(last_cmd, {"success": 0, "failure": 0})
            total = pattern_stat["success"] + pattern_stat["failure"]
            neural_confidence = pattern_stat["success"] / total if total > 0 else 0.5
            
            self.state.diagnostic_report["neural_confidence_score"] = round(neural_confidence, 3)

        return self.state
