import time
import json
from typing import Dict, Any, Optional
from clide.control.permissions import ControlPermissionModel, ControlRole, ActionType
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType

class ControlRouter:
    """
    Controller as a router, not a god object.
    Authenticates, validates against policy, routes to engines, and logs interventions.
    """
    def __init__(self, user_role: ControlRole = ControlRole.OBSERVER, policy_engine: Optional[Any] = None):
        self.permissions = ControlPermissionModel(user_role)
        self.policy_engine = policy_engine

    def handle_command(self, action: ActionType, target_id: str, payload: Dict[str, Any], trace_id: Optional[str] = None):
        """
        Main entry point for all control interventions.
        """
        # 1. Permission check
        self.permissions.validate_action(action)

        # 2. Policy check
        if self.policy_engine:
            self.policy_engine.validate_intervention(action, target_id, payload)

        # 3. Log intervention (Audit Trail)
        audit_entry = self.permissions.get_audit_entry(action, target_id, payload)
        audit_entry["timestamp"] = time.time()
        
        # Emit INTERVENTION event via syscalls
        syscalls.cap_event_commit(
            trace_id=trace_id or "system_control",
            layer=Layer.CAP,
            event_type="SYSTEM_INTERVENTION",
            payload=audit_entry
        )

        # 4. Route to subsystems (to be implemented)
        return self._route(action, target_id, payload, trace_id)

    def _route(self, action: ActionType, target_id: str, payload: Dict[str, Any], trace_id: Optional[str]):
        """
        Dispatches to correct subsystem engines.
        """
        if action == ActionType.INJECT_GOAL:
            # Route to goal manager (to be implemented)
            print(f"[*] ROUTING: Inject goal '{payload.get('goal')}' to goal manager.")
            pass
        elif action == ActionType.INTERVENE_AGENT:
            # Route to influence engine or agent manager
            print(f"[*] ROUTING: Intervene agent '{target_id}' with influence '{payload.get('type')}'")
            pass
        elif action == ActionType.MODIFY_POLICY:
             # Route to policy engine
             print(f"[*] ROUTING: Modify policy '{target_id}'")
             pass
        return {"status": "success", "action": action.value, "target": target_id}
