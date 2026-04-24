import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GoalOrigin(Enum):
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"

class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    priority: float = 0.5 # 0.0 - 1.0
    ttl: int = 3600 # 1 hour default
    origin: GoalOrigin = GoalOrigin.USER
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"

class GoalManager:
    """
    Goal Arbitration System.
    Manages competing goals, priorities, and TTL.
    """
    def __init__(self):
        self.active_goals: Dict[str, Goal] = {}

    def inject_goal(self, goal_text: str, priority: float = 0.5, ttl: int = 3600, origin: GoalOrigin = GoalOrigin.USER):
        goal = Goal(text=goal_text, priority=priority, ttl=ttl, origin=origin)
        self.active_goals[goal.id] = goal
        print(f"[*] GOAL_MANAGER: Injected goal '{goal_text}' with priority {priority}")
        return goal.id

    def get_highest_priority_goal(self) -> Optional[Goal]:
        if not self.active_goals:
             return None
        # Sort by priority, then by age
        sorted_goals = sorted(self.active_goals.values(), key=lambda g: (g.priority, -g.created_at), reverse=True)
        return sorted_goals[0]

    def cleanup_goals(self):
        """Removes expired or completed goals."""
        current_time = time.time()
        to_remove = []
        for gid, goal in self.active_goals.items():
            if current_time - goal.created_at > goal.ttl:
                 print(f"[*] GOAL_MANAGER: Goal {gid[:8]} expired.")
                 to_remove.append(gid)
            elif goal.status == "completed":
                 to_remove.append(gid)
                 
        for gid in to_remove:
            del self.active_goals[gid]

    def update_goal_status(self, goal_id: str, status: str):
        if goal_id in self.active_goals:
             self.active_goals[goal_id].status = status
