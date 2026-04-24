import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional, Set, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

class NodeType(Enum):
    GOAL = "GOAL"
    HYPOTHESIS = "HYPOTHESIS"
    FACT = "FACT"
    PLAN = "PLAN"
    ACTION = "ACTION"
    INFERENCE = "INFERENCE"

class EdgeType(Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    TRIGGERS = "TRIGGERS"
    REFINES = "REFINES"
    CAUSES = "CAUSES"
    PART_OF = "PART_OF"

class CognitiveNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    confidence: float = 1.0
    agent_id: str = "prime"
    trace_id: Optional[str] = None

class CognitiveEdge(BaseModel):
    source_id: str
    target_id: str
    type: EdgeType
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)

class CognitiveStateGraph:
    """
    The unified 'world model' for CAP agents.
    Provides a graph-based representation of the system's current understanding,
    goals, and plans.
    """
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id
        self.nodes: Dict[str, CognitiveNode] = {}
        self.edges: List[CognitiveEdge] = []
        self._index_by_type: Dict[NodeType, Set[str]] = {t: set() for t in NodeType}
        
    def add_node(self, node: CognitiveNode) -> str:
        self.nodes[node.id] = node
        self._index_by_type[node.type].add(node.id)
        return node.id

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, weight: float = 1.0, metadata: Dict[str, Any] = None) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            # In a real system, we might want to allow dangling edges or auto-create nodes
            # For now, let's just log a warning if we were logging.
            pass
        edge = CognitiveEdge(source_id=source_id, target_id=target_id, type=edge_type, weight=weight, metadata=metadata or {})
        self.edges.append(edge)

    def get_nodes_by_type(self, node_type: NodeType) -> List[CognitiveNode]:
        return [self.nodes[nid] for nid in self._index_by_type[node_type]]

    def get_active_goals(self) -> List[CognitiveNode]:
        return [n for n in self.get_nodes_by_type(NodeType.GOAL) if n.metadata.get("status") == "ACTIVE"]

    def get_context_window(self, agent_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Returns a filtered view of the state graph relevant to a specific agent.
        """
        # Simple implementation: return recent nodes and those related to the agent
        relevant_nodes = [n for n in self.nodes.values() if n.agent_id == agent_id or n.agent_id == "prime"]
        relevant_nodes.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {
            "nodes": [n.dict() for n in relevant_nodes[:limit]],
            "recent_facts": [n.dict() for n in self.get_nodes_by_type(NodeType.FACT)][-limit:],
            "active_goals": [n.dict() for n in self.get_active_goals()]
        }

    def commit_fact(self, content: Any, confidence: float = 1.0, metadata: Dict[str, Any] = None, agent_id: str = "prime"):
        node = CognitiveNode(
            type=NodeType.FACT,
            content=content,
            confidence=confidence,
            metadata=metadata or {},
            agent_id=agent_id,
            trace_id=self.trace_id
        )
        return self.add_node(node)

    def propose_hypothesis(self, content: Any, parent_id: Optional[str] = None, agent_id: str = "prime"):
        node = CognitiveNode(
            type=NodeType.HYPOTHESIS,
            content=content,
            agent_id=agent_id,
            trace_id=self.trace_id
        )
        node_id = self.add_node(node)
        if parent_id:
            self.add_edge(node_id, parent_id, EdgeType.REFINES)
        return node_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "nodes": {nid: n.dict() for nid, n in self.nodes.items()},
            "edges": [e.dict() for e in self.edges]
        }

    def validate_consistency(self) -> List[str]:
        """
        Perform consistency checks on the state graph.
        Returns a list of warnings/errors.
        """
        issues = []
        # 1. Check for contradictory edges
        for edge in self.edges:
            if edge.type == EdgeType.CONTRADICTS:
                issues.append(f"Contradiction detected between {edge.source_id} and {edge.target_id}")
        
        # 2. Check for goals without supporting plans
        goals = self.get_active_goals()
        for goal in goals:
            has_plan = any(e.target_id == goal.id and e.type == EdgeType.SUPPORTS for e in self.edges)
            if not has_plan:
                issues.append(f"Active goal {goal.id[:8]} has no supporting plan.")
                
        return issues

    def get_state_evolution(self) -> List[Dict[str, Any]]:
        """
        Returns a chronological list of state transitions.
        """
        # Simplistic view: all nodes and edges sorted by timestamp
        timeline = []
        for n in self.nodes.values():
            timeline.append({"type": "NODE_ADDED", "timestamp": n.timestamp, "data": n.dict()})
        for e in self.edges:
            timeline.append({"type": "EDGE_ADDED", "timestamp": e.timestamp, "data": e.dict()})
        
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline
