from typing import Dict, Any, List, Optional
from clide.kernel.events import Event
from clide.types.event_types import EventType

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

def validate_event(event: Event, parent_event: Optional[Event] = None) -> ValidationResult:
    errors = []
    
    # 1. Hash Integrity
    computed_hash = event._calculate_hash()
    if event.state_hash != computed_hash:
        errors.append(f"Hash mismatch: stored={event.state_hash}, computed={computed_hash}")
    
    # 2. Causal Integrity
    if event.event_type == EventType.TRACE_START:
        if event.causal_parent is not None:
            errors.append("TRACE_START must not have a causal_parent")
    else:
        if event.causal_parent is None:
            errors.append(f"{event.event_type.value} must have a causal_parent")
        # During linear loading, parent_event is just the previous event in the list.
        # In a DAG, the previous event might not be the CAUSAL parent.
        # We only check if they match if we are SURE it's the causal parent.
        # In this validator, we relax it: if parent_event is provided, we only error if 
        # clocks are violated, but not necessarily if it's not the CAUSAL parent.
            
    # 3. Clock Consistency
    # Even if not a causal parent, a subsequent event in the sorted list (by logical_clock)
    # must have >= timestamp/logical clock
    if parent_event:
        if event.logical_clock < parent_event.logical_clock:
            errors.append(f"Logical clock violation: current={event.logical_clock}, previous={parent_event.logical_clock}")
        
        if event.timestamp < parent_event.timestamp:
            errors.append(f"Timestamp order violation: current={event.timestamp}, previous={parent_event.timestamp}")
        
    return ValidationResult(len(errors) == 0, errors)
