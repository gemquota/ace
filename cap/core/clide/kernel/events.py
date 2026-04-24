import uuid
import json
import hashlib
import os
from typing import Optional, Dict, Any
from clide.types.event_types import Layer, EventType

def get_node_id():
    return os.environ.get("CAP_NODE_ID", "default_node")

class Event:
    def __init__(
        self,
        trace_id: str,
        layer: Layer,
        event_type: EventType,
        payload: Dict[str, Any],
        timestamp: int,
        logical_clock: int,
        node_id: Optional[str] = None,
        causal_parent: Optional[str] = None,
        event_id: Optional[str] = None,
        state_hash: Optional[str] = None
    ):
        self.event_id = event_id or str(uuid.uuid4())
        self.trace_id = trace_id
        self.node_id = node_id or get_node_id()
        self.timestamp = timestamp
        self.logical_clock = logical_clock
        self.layer = layer
        self.event_type = event_type
        self.payload = payload
        self.causal_parent = causal_parent
        self.state_hash = state_hash or self._calculate_hash()

    def _calculate_hash(self) -> str:
        data = {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "logical_clock": self.logical_clock,
            "layer": self.layer.value if isinstance(self.layer, Layer) else self.layer,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "payload": self.payload,
            "causal_parent": self.causal_parent
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "logical_clock": self.logical_clock,
            "layer": self.layer.value if isinstance(self.layer, Layer) else self.layer,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "payload": json.dumps(self.payload),
            "causal_parent": self.causal_parent,
            "state_hash": self.state_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        payload = json.loads(data["payload"]) if isinstance(data["payload"], str) else data["payload"]
        return cls(
            event_id=data["event_id"],
            trace_id=data["trace_id"],
            node_id=data["node_id"],
            timestamp=data["timestamp"],
            logical_clock=data["logical_clock"],
            layer=Layer(data["layer"]),
            event_type=EventType(data["event_type"]),
            payload=payload,
            causal_parent=data["causal_parent"],
            state_hash=data["state_hash"]
        )
