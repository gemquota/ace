from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ActionNode:
    action_id: str
    command: str
    dependencies: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    importance: float = 5.0

@dataclass
class IntentDAG:
    intent_id: str
    goal: str
    actions: List[ActionNode] = field(default_factory=list)
    context_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "goal": self.goal,
            "actions": [
                {
                    "action_id": a.action_id,
                    "command": a.command,
                    "dependencies": a.dependencies,
                    "constraints": a.constraints,
                    "importance": a.importance
                } for a in self.actions
            ],
            "context_refs": self.context_refs,
            "metadata": self.metadata
        }
