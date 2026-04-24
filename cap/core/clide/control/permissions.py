from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field

class ControlRole(Enum):
    OBSERVER = "OBSERVER"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"

class ActionType(Enum):
    READ = "READ"
    INTERVENE_AGENT = "INTERVENE_AGENT"
    INJECT_GOAL = "INJECT_GOAL"
    MODIFY_POLICY = "MODIFY_POLICY"
    ROLLBACK_SYSTEM = "ROLLBACK_SYSTEM"
    SIMULATE = "SIMULATE"

ROLE_PERMISSIONS: Dict[ControlRole, Set[ActionType]] = {
    ControlRole.OBSERVER: {ActionType.READ},
    ControlRole.OPERATOR: {
        ActionType.READ,
        ActionType.INTERVENE_AGENT,
        ActionType.INJECT_GOAL,
        ActionType.SIMULATE
    },
    ControlRole.ADMIN: {
        ActionType.READ,
        ActionType.INTERVENE_AGENT,
        ActionType.INJECT_GOAL,
        ActionType.MODIFY_POLICY,
        ActionType.ROLLBACK_SYSTEM,
        ActionType.SIMULATE
    }
}

class ControlPermissionModel:
    """
    Structured, permissioned, and auditable control system.
    """
    def __init__(self, user_role: ControlRole = ControlRole.OBSERVER):
        self.user_role = user_role

    def can_perform(self, action: ActionType) -> bool:
        return action in ROLE_PERMISSIONS.get(self.user_role, set())

    def validate_action(self, action: ActionType):
        if not self.can_perform(action):
            raise PermissionError(f"Role {self.user_role.value} cannot perform {action.value}")
        return True

    def get_audit_entry(self, action: ActionType, target_id: str, payload: Dict[str, Any]):
        return {
            "role": self.user_role.value,
            "action": action.value,
            "target": target_id,
            "payload": payload,
            "timestamp": None # To be filled by caller
        }
