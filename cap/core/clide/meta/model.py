import json
from typing import Dict, Any, List, Optional
from clide.types.event_types import Layer, EventType
from clide.kernel import syscalls

class Subsystem:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.metrics = {
            "efficiency": 1.0,
            "success_rate": 1.0,
            "latency": 0.0,
            "error_count": 0
        }

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "metrics": self.metrics
        }

class SelfArchitectureModel:
    def __init__(self):
        self.version = "1.0.0"
        self.subsystems = {
            "CLIDE": Subsystem("CLIDE", "Intent Compilation"),
            "APC": Subsystem("APC", "Action Execution"),
            "PIE": Subsystem("PIE", "Inference & Analysis"),
            "MEMORY": Subsystem("MEMORY", "Historical Learning"),
            "ORCHESTRATOR": Subsystem("ORCHESTRATOR", "Planning & Scheduling"),
            "SOVEREIGN": Subsystem("SOVEREIGN", "Autonomous Goal Generation")
        }
        self.meta_metrics = {
            "learning_efficiency": 0.0,
            "planning_accuracy": 0.0,
            "execution_variance": 0.0,
            "explore_vs_exploit_ratio": 0.5
        }
        self.config_overrides = {}

    def update_metrics(self, subsystem_name: str, new_metrics: Dict[str, Any]):
        if subsystem_name in self.subsystems:
            self.subsystems[subsystem_name].metrics.update(new_metrics)

    def to_dict(self):
        return {
            "version": self.version,
            "subsystems": {k: v.to_dict() for k, v in self.subsystems.items()},
            "meta_metrics": self.meta_metrics,
            "config_overrides": self.config_overrides
        }

    def save(self, path="clide_arch_model.json"):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path="clide_arch_model.json"):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                model = cls()
                model.version = data.get("version", "1.0.0")
                model.meta_metrics = data.get("meta_metrics", {})
                model.config_overrides = data.get("config_overrides", {})
                
                # Load subsystems
                subsystems_data = data.get("subsystems", {})
                for name, s_data in subsystems_data.items():
                    if name in model.subsystems:
                        model.subsystems[name].metrics = s_data.get("metrics", {})
                return model
        except:
            return cls()
