from typing import List, Dict, Any, Optional
from clide.storage import db
import json

class ExplainabilityEngine:
    """
    Causal Tracing Depth Control.
    Clarity vs. Completeness.
    """
    def __init__(self):
        pass

    def explain(self, event_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        Explains an event by tracing its causal parents.
        Depth 1: immediate cause
        Depth 3: reasoning chain
        Depth 5+: full causal graph
        """
        explanation = self._trace_causality(event_id, depth)
        return {
            "event_id": event_id,
            "depth": depth,
            "chain": explanation
        }

    def _trace_causality(self, event_id: str, depth: int) -> List[Dict[str, Any]]:
        if depth <= 0:
            return []
            
        with db.get_connection() as conn:
            row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
            if not row:
                return []
                
            event_dict = dict(row)
            parent_id = event_dict.get("causal_parent")
            
            explanation = [{
                "id": event_id,
                "type": event_dict.get("event_type"),
                "payload": json.loads(event_dict["payload"]) if isinstance(event_dict["payload"], str) else event_dict["payload"],
                "timestamp": event_dict.get("timestamp")
            }]
            
            if parent_id:
                 explanation.extend(self._trace_causality(parent_id, depth - 1))
                 
            return explanation
