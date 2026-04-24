import json
from typing import List, Dict, Any, Optional
from .model import SelfArchitectureModel
from .evaluator import ArchProposal

class Experiment:
    def __init__(self, proposal: ArchProposal):
        self.proposal = proposal
        self.start_time = None
        self.end_time = None
        self.results = [] # Success rate, latency, etc.
        self.is_active = False

class ExperimentFramework:
    def __init__(self, model: SelfArchitectureModel):
        self.model = model
        self.active_experiments = []

    def run_experiment(self, proposal: ArchProposal):
        print(f"[*] META: Starting Experiment: {proposal.change} for {proposal.subsystem}")
        experiment = Experiment(proposal)
        experiment.is_active = True
        # Apply change as config override
        self.model.config_overrides[f"{proposal.subsystem}.{proposal.change}"] = proposal.params
        self.active_experiments.append(experiment)

    def evaluate_experiment(self, experiment: Experiment, metrics: Dict[str, Any]) -> bool:
        """
        Return True if successful and should be adopted.
        """
        # (Simplified) Compare metrics before and during experiment
        # If metrics improved, return True
        # For now, if metrics success_rate > 0.8, adopt
        return metrics.get("success_rate", 0.0) > 0.8

    def adopt_proposal(self, proposal: ArchProposal):
        print(f"[*] META: Adopting ARCH_PROPOSAL: {proposal.change}")
        proposal.status = "ADOPTED"
        # Permanently apply to config
        # (Implementation of permanent config would go here)

    def rollback_proposal(self, proposal: ArchProposal):
        print(f"[*] META: Rolling back ARCH_PROPOSAL: {proposal.change}")
        proposal.status = "ROLLED_BACK"
        if f"{proposal.subsystem}.{proposal.change}" in self.model.config_overrides:
            del self.model.config_overrides[f"{proposal.subsystem}.{proposal.change}"]
