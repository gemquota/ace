from typing import List, Dict, Any
from clide.storage import db
from clide.kernel.events import Event
from clide.kernel.validator import validate_event

class PieEngine:
    def __init__(self):
        pass

    def load_trace(self, trace_id: str) -> List[Event]:
        raw_events = db.get_events_by_trace(trace_id)
        events = [Event.from_dict(e) for e in raw_events]
        
        # Basic validation of the trace as it's loaded
        for i, ev in enumerate(events):
            parent = events[i-1] if i > 0 else None
            res = validate_event(ev, parent)
            if not res.is_valid:
                raise ValueError(f"Trace {trace_id} is corrupted at event {ev.event_id}: {res.errors}")
                
        return events
