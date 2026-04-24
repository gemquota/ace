from typing import Dict, Any, List, Optional, Callable

class HITLManager:
    """
    Human-In-The-Loop Trigger System.
    Scarce and high-value user intervention.
    """
    def __init__(self, request_callback: Callable[[Dict[str, Any]], Any]):
        self.request_callback = request_callback
        self.pending_decisions: Dict[str, Any] = {}

    def should_ask_human(self, context: Dict[str, Any]) -> bool:
        """
        Determines if human intervention is necessary.
        """
        # Trigger conditions
        confidence = context.get("confidence", 1.0)
        impact = context.get("impact", 0.0) # Heuristic for potential damage
        policy_conflicts = context.get("policy_conflicts", [])

        if confidence < 0.4: return True # Low-confidence
        if impact > 0.8: return True # High-impact
        if policy_conflicts: return True # Conflicting policies
        
        return False

    async def request_human_input(self, decision_id: str, context: Dict[str, Any]):
        """
        Requests input from the user.
        """
        if self.should_ask_human(context):
             print(f"[?] HITL: Intervention required for decision {decision_id}.")
             return await self.request_callback(context)
        return None
