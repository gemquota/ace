import uuid
import time
import os
from typing import Dict, Any, Optional
from clide.storage import db
from clide.kernel.events import Event, get_node_id
from clide.kernel.clock import get_next_logical_time, get_real_timestamp, update_clock
from clide.types.event_types import Layer, EventType
from clide.kernel.validator import validate_event
from clide.kernel.identity import init_genesis

def cap_trace_start() -> str:
    db.register_node(get_node_id())
    trace_id = str(uuid.uuid4())
    
    # Phase 19: Identity & Rollback Infrastructure
    # Anchor Genesis Hash to the first trace start
    init_genesis(trace_id)
    
    created_at = get_real_timestamp()
    db.commit_trace(trace_id, created_at)
    
    # Emit TRACE_START event
    event = Event(
        trace_id=trace_id,
        layer=Layer.CAP,
        event_type=EventType.TRACE_START,
        payload={"created_at": created_at},
        timestamp=created_at,
        logical_clock=get_next_logical_time()
    )
    db.commit_event(event.to_dict())
    return trace_id

def spawn_agent_trace(parent_trace_id: str, agent_id: str) -> str:
    """Spawn a child trace for a specific agent branching from a parent trace."""
    db.register_node(get_node_id())
    child_trace_id = f"{parent_trace_id}_agent_{agent_id[:8]}"
    created_at = get_real_timestamp()
    db.commit_trace(child_trace_id, created_at)
    
    cap_event_commit(
        trace_id=child_trace_id,
        layer=Layer.CAP,
        event_type=EventType.TRACE_START,
        payload={"parent_trace_id": parent_trace_id, "agent_id": agent_id},
        causal_parent=None # Root of branch
    )
    return child_trace_id

def cap_event_commit(
    trace_id: str,
    layer: Layer,
    event_type: EventType,
    payload: Dict[str, Any],
    causal_parent: Optional[str] = None
) -> str:
    db.register_node(get_node_id())
    event = Event(
        trace_id=trace_id,
        layer=layer,
        event_type=event_type,
        payload=payload,
        timestamp=get_real_timestamp(),
        logical_clock=get_next_logical_time(),
        causal_parent=causal_parent
    )
    
    db.commit_event(event.to_dict())
    return event.event_id

def cap_trace_end(trace_id: str, causal_parent: str):
    cap_event_commit(
        trace_id=trace_id,
        layer=Layer.CAP,
        event_type=EventType.TRACE_END,
        payload={"ended_at": get_real_timestamp()},
        causal_parent=causal_parent
    )

def cap_validate_event(event_dict: Dict[str, Any], parent_dict: Optional[Dict[str, Any]] = None):
    event = Event.from_dict(event_dict)
    parent = Event.from_dict(parent_dict) if parent_dict else None
    return validate_event(event, parent)

def cap_list_nodes():
    return db.get_nodes()
