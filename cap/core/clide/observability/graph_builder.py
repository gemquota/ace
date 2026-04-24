from typing import List, Dict, Any, Optional, Set
from clide.observability.models import CognitiveEvent, CausalEdge, RelationshipType
from clide.storage import db
import json

class GraphBuilder:
    """
    Constructs high-level visualization graphs.
    """
    def __init__(self):
        pass

    def build_causal_graph(self, trace_id: str) -> Dict[str, Any]:
        """
        Builds a causal graph of all events in a trace.
        """
        nodes = []
        edges = []
        with db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM events WHERE trace_id = ? ORDER BY logical_clock ASC", (trace_id,)).fetchall()
            for row in rows:
                event_id = row["event_id"]
                event_type = row["event_type"]
                causal_parent = row["causal_parent"]
                nodes.append({
                    "id": event_id,
                    "label": event_type,
                    "data": json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
                })
                if causal_parent:
                    edges.append({
                        "source": causal_parent,
                        "target": event_id,
                        "label": "CAUSED"
                    })
        return {"nodes": nodes, "links": edges}

    def build_agent_interaction_graph(self, trace_id: str) -> Dict[str, Any]:
        """
        Builds a graph showing how agents interact (communication, transactions).
        """
        nodes = {} # agent_id -> node_info
        edges = [] # List of interaction edges
        
        with db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM events WHERE trace_id = ?", (trace_id,)).fetchall()
            for row in rows:
                payload = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
                agent_id = payload.get("agent_id") or "prime"
                
                if agent_id not in nodes:
                    nodes[agent_id] = {"id": agent_id, "label": agent_id}
                
                # Check for interactions in payload
                target_agent = payload.get("target_agent_id") or payload.get("to_agent")
                if target_agent:
                    if target_agent not in nodes:
                        nodes[target_agent] = {"id": target_agent, "label": target_agent}
                    edges.append({
                        "source": agent_id,
                        "target": target_agent,
                        "label": row["event_type"]
                    })
        return {"nodes": list(nodes.values()), "links": edges}

    def build_inference_chain(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Extracts all inference events and their relationships.
        """
        chain = []
        with db.get_connection() as conn:
            # Simple linear chain for now
            rows = conn.execute("SELECT * FROM events WHERE trace_id = ? AND (event_type LIKE '%INFERENCE%' OR event_type LIKE '%ANALYSIS%') ORDER BY logical_clock ASC", (trace_id,)).fetchall()
            for row in rows:
                chain.append({
                    "id": row["event_id"],
                    "timestamp": row["timestamp"],
                    "payload": json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
                })
        return chain
