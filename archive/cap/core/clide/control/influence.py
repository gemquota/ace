from typing import Dict, Any, List, Optional
from enum import Enum

class InfluenceType(Enum):
    BIAS_STRATEGY = "BIAS_STRATEGY"
    NUDGE_THRESHOLD = "NUDGE_THRESHOLD"
    BOOST_VISIBILITY = "BOOST_VISIBILITY"
    PENALIZE_REPUTATION = "PENALIZE_REPUTATION"

class InfluenceEngine:
    """
    Soft Influence Layer.
    Steering instead of puppeteering.
    """
    def __init__(self, swarm_manager: Any):
        self.swarm_manager = swarm_manager
        self.active_influences: List[Dict[str, Any]] = []

    def apply_influence(self, agent_id: str, influence_type: InfluenceType, magnitude: float, payload: Dict[str, Any]):
        """
        Nudge an agent's behavior.
        """
        agent = self.swarm_manager.agents.get(agent_id)
        if not agent:
             return {"status": "error", "message": "Agent not found"}
             
        if influence_type == InfluenceType.BIAS_STRATEGY:
             # Increase probability of certain genome behaviors
             # For example, nudge risk_tolerance
             target_param = payload.get("parameter", "risk_tolerance")
             if hasattr(agent.genome, target_param):
                  current_val = getattr(agent.genome, target_param)
                  new_val = max(0.0, min(1.0, current_val + (magnitude * 0.1)))
                  setattr(agent.genome, target_param, new_val)
                  print(f"[*] INFLUENCE: Nudged {agent_id[:8]} parameter {target_param} to {new_val:.2f}")

        elif influence_type == InfluenceType.BOOST_VISIBILITY:
             # Make agent more likely to be selected for tasks
             agent.performance_score += magnitude * 0.1
             print(f"[*] INFLUENCE: Boosted visibility of {agent_id[:8]} by {magnitude}")

        return {"status": "success", "agent_id": agent_id}
