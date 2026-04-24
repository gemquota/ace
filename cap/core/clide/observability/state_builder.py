from typing import Dict, Any, List, Optional
from clide.state_graph import CognitiveStateGraph, NodeType, CognitiveNode
from clide.observability.models import CognitiveEvent, AgentState, AgentStatus
from clide.storage import db
import json

class StateBuilder:
    """
    Constructs a snapshot of the system's cognitive state.
    """
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id
        self.graph = CognitiveStateGraph(trace_id=trace_id)
        self.agent_states: Dict[str, AgentState] = {}

    def update_from_event(self, cog_event: CognitiveEvent):
        # Update the graph based on the cognitive event
        node_type = NodeType.FACT
        if cog_event.type.value == "DECISION":
            node_type = NodeType.GOAL
        elif cog_event.type.value == "INFERENCE":
            node_type = NodeType.INFERENCE
        elif cog_event.type.value == "ACTION":
            node_type = NodeType.ACTION
            
        node = CognitiveNode(
            id=cog_event.id,
            type=node_type,
            content=cog_event.payload,
            metadata=cog_event.payload,
            timestamp=cog_event.timestamp,
            confidence=cog_event.confidence,
            agent_id=cog_event.agent_id,
            trace_id=cog_event.trace_id
        )
        self.graph.add_node(node)
        
        # Link to parents
        for parent_id in cog_event.parent_event_ids:
            # We assume the parent node exists in the graph or we create a placeholder
            self.graph.add_edge(cog_event.id, parent_id, edge_type="CAUSES") # EdgeType.CAUSES

    def update_agent_state(self, agent_state: AgentState):
        self.agent_states[agent_state.agent_id] = agent_state

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "graph": self.graph.to_dict(),
            "agents": {aid: s.dict() for aid, s in self.agent_states.items()},
            "active_goals": [n.dict() for n in self.graph.get_active_goals()]
        }
        
    def rebuild_from_db(self, trace_id: str):
        """
        Reconstructs the state from all events in a trace.
        """
        self.trace_id = trace_id
        self.graph = CognitiveStateGraph(trace_id=trace_id)
        from clide.observability.aggregator import ObservabilityAggregator
        agg = ObservabilityAggregator()
        
        with db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM events WHERE trace_id = ? ORDER BY logical_clock ASC", (trace_id,)).fetchall()
            for row in rows:
                raw_event = dict(row)
                cog_event = agg.normalize_raw_event(raw_event)
                if cog_event:
                    self.update_from_event(cog_event)
                    agent_state = agg.extract_agent_state(cog_event)
                    if agent_state:
                        self.update_agent_state(agent_state)
