from typing import List, Dict, Any, Optional
from .model import SelfArchitectureModel

class ArchProposal:
    def __init__(self, subsystem: str, change: str, expected_impact: str, params: Dict[str, Any]):
        self.subsystem = subsystem
        self.change = change
        self.expected_impact = expected_impact
        self.params = params
        self.status = "PENDING" # PENDING, ADOPTED, REJECTED, ROLLED_BACK

    def to_dict(self):
        return self.__dict__

class ArchitectureEvaluator:
    def __init__(self, model: SelfArchitectureModel):
        self.model = model

    def evaluate(self) -> List[ArchProposal]:
        proposals = []
        
        # 1. Evaluate PIE (Inference & Analysis)
        pie = self.model.subsystems["PIE"]
        if pie.metrics["success_rate"] < 0.7:
            proposals.append(ArchProposal(
                subsystem="PIE",
                change="increase_analysis_depth",
                expected_impact="reduce_anomaly_miss_rate",
                params={"max_flavours": 10, "causal_threshold": 0.5}
            ))

        # 2. Evaluate APC (Action Execution)
        apc = self.model.subsystems["APC"]
        if apc.metrics["efficiency"] < 0.5:
            proposals.append({
                "subsystem": "APC",
                "type": "THROTTLE",
                "change": "reduce_concurrency",
                "expected_impact": "increase_success_rate",
                "params": {"max_workers": 1}
            })

        # 3. Evaluate ORCHESTRATOR (Planning & Scheduling)
        orch = self.model.subsystems["ORCHESTRATOR"]
        if orch.metrics["efficiency"] < 0.5:
            proposals.append(ArchProposal(
                subsystem="ORCHESTRATOR",
                change="parallel_dispatch",
                expected_impact="increase_execution_throughput",
                params={"max_workers": 8}
            ))

        # 3. Evaluate MEMORY (Historical Learning)
        mem = self.model.subsystems["MEMORY"]
        if self.model.meta_metrics["learning_efficiency"] < 0.3:
            proposals.append(ArchProposal(
                subsystem="MEMORY",
                change="increase_pattern_decay_rate",
                expected_impact="reduce_stale_pattern_interference",
                params={"decay_rate": 0.2}
            ))

        # 4. SOVEREIGN (Autonomous Goal Generation)
        # If goals are too risky, decrease risk tolerance
        return proposals

    def get_meta_goals(self) -> List[Dict[str, Any]]:
        """
        Generate goals for the Sovereign engine to test the system.
        """
        meta_goals = []
        if self.model.subsystems["APC"].metrics["efficiency"] < 0.5:
            meta_goals.append({
                "primitive": "diagnose_apc",
                "goal": "verify_sandbox_integrity",
                "reason": "LOW_APC_EFFICIENCY"
            })
        if self.model.meta_metrics.get("planning_accuracy", 1.0) < 0.5:
            meta_goals.append({
                "primitive": "stress_test_planner",
                "goal": "generate_complex_dag",
                "reason": "IMPROVE_PLANNING_ACCURACY"
            })
        return meta_goals
