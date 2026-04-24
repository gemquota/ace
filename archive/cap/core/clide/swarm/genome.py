import random
from enum import Enum
from typing import List, Dict, Any, Optional

class AgentStrategy(Enum):
    EXPLORER = "EXPLORER"
    PLANNER = "PLANNER"
    EXECUTOR = "EXECUTOR"
    CONSERVATIVE = "CONSERVATIVE"
    ADAPTIVE = "ADAPTIVE"

class Genome:
    """
    Defines the evolvable behavioral parameters of an agent.
    Influences decision thresholds, planner behavior, and resource usage.
    """
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        if data is None:
            # Default/Random Genesis Genome
            self.strategy = random.choice(list(AgentStrategy))
            self.risk_tolerance = random.uniform(0.1, 0.9)
            self.exploration_rate = random.uniform(0.1, 0.5)
            self.memory_weight = random.uniform(0.3, 0.9)
            self.cooperation_bias = random.uniform(0.1, 0.9)
            self.model_preferences = random.sample(["causal", "predictive", "diagnostic", "neural_alignment"], 2)
            self.mutation_rate = 0.1
        else:
            self.strategy = AgentStrategy(data.get("strategy", "ADAPTIVE"))
            self.risk_tolerance = data.get("risk_tolerance", 0.5)
            self.exploration_rate = data.get("exploration_rate", 0.2)
            self.memory_weight = data.get("memory_weight", 0.6)
            self.cooperation_bias = data.get("cooperation_bias", 0.5)
            self.model_preferences = data.get("model_preferences", ["causal", "predictive"])
            self.mutation_rate = data.get("mutation_rate", 0.1)

    def apply(self, agent: Any):
        """Applies genome parameters to a runtime agent instance."""
        agent.strategy = self.strategy
        agent.risk_tolerance = self.risk_tolerance
        agent.exploration_rate = self.exploration_rate
        agent.memory_weight = self.memory_weight
        agent.cooperation_bias = self.cooperation_bias
        agent.model_preferences = self.model_preferences

    def mutate(self) -> 'Genome':
        """Creates a mutated copy of the genome."""
        new_data = self.to_dict()
        
        # Parameter Drift
        if random.random() < self.mutation_rate:
            new_data["risk_tolerance"] = max(0.0, min(1.0, self.risk_tolerance + random.gauss(0, 0.1)))
        if random.random() < self.mutation_rate:
            new_data["exploration_rate"] = max(0.0, min(1.0, self.exploration_rate + random.gauss(0, 0.05)))
        if random.random() < self.mutation_rate:
            new_data["memory_weight"] = max(0.0, min(1.0, self.memory_weight + random.gauss(0, 0.1)))
        
        # Strategy Swap
        if random.random() < self.mutation_rate * 0.5:
            new_data["strategy"] = random.choice(list(AgentStrategy)).value
            
        # Model Preference Shift
        if random.random() < self.mutation_rate:
            models = ["causal", "predictive", "diagnostic", "neural_alignment"]
            new_data["model_preferences"] = random.sample(models, 2)

        return Genome(new_data)

    @classmethod
    def recombine(cls, parent_a: 'Genome', parent_b: 'Genome') -> 'Genome':
        """Sexual recombination of two genomes."""
        data_a = parent_a.to_dict()
        data_b = parent_b.to_dict()
        child_data = {}
        
        for key in data_a:
            child_data[key] = random.choice([data_a[key], data_b[key]])
            
        return cls(child_data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "risk_tolerance": self.risk_tolerance,
            "exploration_rate": self.exploration_rate,
            "memory_weight": self.memory_weight,
            "cooperation_bias": self.cooperation_bias,
            "model_preferences": self.model_preferences,
            "mutation_rate": self.mutation_rate
        }
