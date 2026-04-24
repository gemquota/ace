import uuid
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from clide.schema import ActionNode, IntentDAG
from pie.inference import InferenceState
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from clide.state_graph import CognitiveStateGraph

class StrategyMode(Enum):
    AGGRESSIVE = "AGGRESSIVE"
    CONSERVATIVE = "CONSERVATIVE"
    ADAPTIVE = "ADAPTIVE"

@dataclass
class OrchestrationState:
    trace_id: str
    dag: IntentDAG
    strategy: StrategyMode = StrategyMode.CONSERVATIVE
    active_nodes: Set[str] = field(default_factory=set)
    completed_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)
    inferred_state: Optional[InferenceState] = None
    state_graph: Optional[CognitiveStateGraph] = None

class PlanMutationEngine:
    def __init__(self, state: OrchestrationState):
        self.state = state

    def insert_node(self, node: ActionNode, before_node_id: Optional[str] = None):
        """
        Inserts a new ActionNode into the DAG.
        If before_node_id is provided, the new node becomes a dependency for it.
        """
        # Add to DAG actions
        self.state.dag.actions.append(node)
        
        if before_node_id:
            # Find the node to insert before
            for n in self.state.dag.actions:
                if n.action_id == before_node_id:
                    n.dependencies.append(node.action_id)
                    break
                    
        # Emit ACTION_INSERTED
        syscalls.cap_event_commit(
            trace_id=self.state.trace_id,
            layer=Layer.CAP,
            event_type=EventType.ACTION_INSERTED,
            payload={"action_id": node.action_id, "command": node.command},
            causal_parent=None # Should link to trigger
        )
        
        # Emit PLAN_MUTATION
        syscalls.cap_event_commit(
            trace_id=self.state.trace_id,
            layer=Layer.CAP,
            event_type=EventType.PLAN_MUTATION,
            payload={"mutation_type": "INSERT", "action_id": node.action_id},
            causal_parent=None
        )

    def skip_node(self, node_id: str):
        """Marks a node as completed without actually running it."""
        self.state.completed_nodes.add(node_id)
        syscalls.cap_event_commit(
            trace_id=self.state.trace_id,
            layer=Layer.CAP,
            event_type=EventType.ACTION_SKIPPED,
            payload={"action_id": node_id},
            causal_parent=None
        )

    def suggest_corrections(self, failed_node: ActionNode, inference: InferenceState) -> List[ActionNode]:
        """
        Analyze PIE diagnostic and suggest corrective nodes.
        """
        corrections = []
        if not inference or not inference.diagnostic_report:
            return corrections
            
        report = inference.diagnostic_report
        # Example: if probable_causes mentions a missing dependency
        causes = str(report.get("probable_causes", [])).lower()
        
        if "missing" in causes or "not found" in causes:
            # Heuristic for missing dependency
            # This would be more advanced in a real system
            if "git" in failed_node.command:
                corrections.append(ActionNode(
                    action_id=f"heal_{str(uuid.uuid4())[:8]}",
                    command="apt update && apt install -y git",
                    importance=10.0
                ))
            elif "mkdir" in causes:
                 corrections.append(ActionNode(
                    action_id=f"heal_{str(uuid.uuid4())[:8]}",
                    command="mkdir -p $(dirname " + failed_node.command.split()[-1] + ")",
                    importance=10.0
                ))
                
        return corrections

    def update_strategy(self, mode: StrategyMode):
        if self.state.strategy != mode:
            self.state.strategy = mode
            syscalls.cap_event_commit(
                trace_id=self.state.trace_id,
                layer=Layer.CAP,
                event_type=EventType.STRATEGY_SWITCH,
                payload={"new_strategy": mode.value},
                causal_parent=None
            )
