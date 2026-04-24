from typing import Dict, Any, Optional

class FitnessEvaluator:
    """
    Evaluates agent performance across multiple timescales and metrics.
    Prevents short-term greedy behavior from dominating the system.
    """
    def __init__(self):
        # Weights for different components
        self.weights = {
            "short_term_success": 0.3,
            "resource_efficiency": 0.2,
            "economic_gain": 0.2,
            "system_contribution": 0.3 # e.g. helping other agents, discovering facts
        }

    def calculate_fitness(self, metrics: Dict[str, Any]) -> float:
        """
        Calculates a global fitness score for an agent.
        metrics = {
            "success_rate": 0.0-1.0,
            "cost_per_task": float,
            "total_earned": float,
            "knowledge_shared": int,
            "peer_rating": float
        }
        """
        # Short-term Success (Success Rate)
        short_term = metrics.get("success_rate", 0.0)
        
        # Resource Efficiency (Normalized cost)
        # Assuming average cost is around 10.0, we normalize it.
        avg_cost = 10.0
        actual_cost = metrics.get("cost_per_task", avg_cost)
        efficiency = max(0.0, 1.0 - (actual_cost / (avg_cost * 2)))
        
        # Economic Gain
        # We look at the relative gain/loss
        economic_gain = min(1.0, metrics.get("total_earned", 0.0) / 100.0)
        
        # System Contribution
        # Heuristic: combine knowledge sharing and peer ratings
        contribution = min(1.0, (metrics.get("knowledge_shared", 0) / 10.0) + (metrics.get("peer_rating", 0.0) / 1.0))

        fitness = (
            self.weights["short_term_success"] * short_term +
            self.weights["resource_efficiency"] * efficiency +
            self.weights["economic_gain"] * economic_gain +
            self.weights["system_contribution"] * contribution
        )
        
        return round(fitness, 4)
