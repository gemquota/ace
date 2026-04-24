import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WorkingMemoryState(BaseModel):
    active_goals: List[Dict[str, Any]] = Field(default_factory=list)
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)
    active_agents: List[Dict[str, Any]] = Field(default_factory=list)
    current_hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    context_window: Dict[str, Any] = Field(default_factory=dict)
    last_updated: float = Field(default_factory=time.time)

class WorkingMemory:
    """
    Manages the short-term, high-attention state of the system.
    Think of this as the system's 'active consciousness'.
    """
    def __init__(self, trace_id: str, capacity: int = 50):
        self.trace_id = trace_id
        self.capacity = capacity
        self.state = WorkingMemoryState()
        self.decay_factor = 0.1 # Example decay for older items

    def update_event(self, event: Dict[str, Any]):
        self.state.recent_events.append(event)
        if len(self.state.recent_events) > self.capacity:
            self.state.recent_events.pop(0)
        self.state.last_updated = time.time()

    def set_goal(self, goal: Dict[str, Any]):
        # Check if goal already exists
        for g in self.state.active_goals:
            if g.get("id") == goal.get("id"):
                g.update(goal)
                return
        self.state.active_goals.append(goal)
        self.state.last_updated = time.time()

    def add_hypothesis(self, hypothesis: Dict[str, Any]):
        self.state.current_hypotheses.append(hypothesis)
        if len(self.state.current_hypotheses) > 10: # Hypotheses are more limited
            self.state.current_hypotheses.pop(0)
        self.state.last_updated = time.time()

    def refresh_context(self, context: Dict[str, Any]):
        self.state.context_window = context
        self.state.last_updated = time.time()

    def get_snapshot(self) -> Dict[str, Any]:
        return self.state.dict()

    def decay_old_entries(self, max_age_seconds: int = 300):
        """Removes entries that are too old to be in working memory."""
        current_time = time.time()
        # Events naturally pop via capacity, but we can also filter by age
        self.state.recent_events = [e for e in self.state.recent_events if current_time - e.get("timestamp", 0) < max_age_seconds]
