import os
import time
import uuid
import asyncio
from enum import Enum
from typing import List, Dict, Any, Optional
from clide.swarm.economy import ComputeCredit
from clide.swarm.ledger import SwarmLedger
from clide.swarm.negotiator import SwarmNegotiator

from clide.swarm.genome import Genome, AgentStrategy
from clide.swarm.fitness import FitnessEvaluator

class AgentState(Enum):
    SPAWNED = "SPAWNED"
    ACTIVE = "ACTIVE"
    STARVING = "STARVING"
    TERMINATED = "TERMINATED"
    ARCHIVED = "ARCHIVED"

class Agent:
    def __init__(self, agent_id: str, name: str = "agent", genome: Optional[Genome] = None, parent_id: Optional[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.parent_id = parent_id
        self.state = AgentState.SPAWNED
        self.genome = genome or Genome()
        self.genome.apply(self) # Apply behavioral parameters
        
        self.economy = ComputeCredit(agent_id)
        self.fitness_evaluator = FitnessEvaluator()
        
        # Detailed Metrics
        self.performance_score = 0.0
        self.success_rate = 1.0
        self.total_tasks = 0
        self.success_count = 0
        self.total_earned = 0.0
        self.total_spent = 0.0
        self.knowledge_shared = 0
        self.peer_rating = 1.0
        self.generation = 0

    def update_performance(self, success_rate: float, cost: float):
        """Update metrics and recalculate global fitness."""
        self.total_tasks += 1
        if success_rate > 0.0:
            self.success_count += 1
        
        self.success_rate = self.success_count / self.total_tasks
        self.total_spent += cost
        
        metrics = {
            "success_rate": self.success_rate,
            "cost_per_task": self.total_spent / self.total_tasks,
            "total_earned": self.total_earned,
            "knowledge_shared": self.knowledge_shared,
            "peer_rating": self.peer_rating
        }
        self.performance_score = self.fitness_evaluator.calculate_fitness(metrics)
        
        # Check for starvation
        balance = self.economy.get_balance()
        if balance < 5.0:
            self.state = AgentState.STARVING
        elif balance <= 0:
            self.state = AgentState.TERMINATED

    def reproduce(self, partner: Optional['Agent'] = None) -> 'Agent':
        """Spawn a child agent via mutation or recombination."""
        child_id = str(uuid.uuid4())
        if partner:
            child_genome = Genome.recombine(self.genome, partner.genome)
            child_name = f"hybrid_{self.name[:4]}_{partner.name[:4]}"
        else:
            child_genome = self.genome.mutate()
            child_name = f"mutant_{self.name}"
            
        child = Agent(child_id, child_name, child_genome, parent_id=self.agent_id)
        child.generation = self.generation + 1
        return child

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "state": self.state.value,
            "balance": self.economy.get_balance(),
            "score": self.performance_score,
            "genome": self.genome.to_dict(),
            "generation": self.generation
        }

class SwarmManager:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.ledger = SwarmLedger()
        self.negotiator = SwarmNegotiator()
        self.max_concurrent_agents = 10
        self.generation_id = 0
        self.spawn_cost = 50.0
        self.selection_threshold = 0.2 # Kill bottom if score < this

    def spawn_agent(self, name: str = "agent", genome: Optional[Genome] = None) -> str:
        agent_id = str(uuid.uuid4())
        agent = Agent(agent_id, name, genome=genome)
        agent.state = AgentState.ACTIVE
        agent.generation = self.generation_id
        self.agents[agent_id] = agent
        print(f"[*] SWARM: Spawned agent {agent_id[:8]} ({name}) at Gen {self.generation_id}")
        return agent_id

    def cleanup_agents(self):
        """Selection pressure: Remove terminated or low-performing agents."""
        to_remove = []
        for aid, agent in self.agents.items():
            if agent.state == AgentState.TERMINATED:
                to_remove.append(aid)
            elif agent.performance_score < self.selection_threshold and agent.total_tasks > 3:
                print(f"[*] SELECTION: Pruning low-performer {aid[:8]} (Score: {agent.performance_score})")
                agent.state = AgentState.ARCHIVED
                to_remove.append(aid)
        
        for aid in to_remove:
            del self.agents[aid]

    def enforce_diversity(self):
        """Prevents monoculture by penalizing similarity or injecting mutants."""
        if not self.agents: return
        
        strategies = [a.genome.strategy for a in self.agents.values()]
        from collections import Counter
        counts = Counter(strategies)
        
        # If one strategy dominates > 70%, inject random mutants
        dominant_threshold = 0.7 * len(self.agents)
        for strat, count in counts.items():
            if count > dominant_threshold and len(self.agents) > 3:
                print(f"[!] DIVERSITY WARNING: Strategy {strat} dominates. Injecting mutants.")
                for _ in range(2):
                    self.spawn_agent(f"diversity_mutant_{strat.value}")

    def trigger_evolution(self):
        """Discrete Generation Update: Evaluate, Select, Reproduce."""
        self.generation_id += 1
        print(f"[*] EVOLUTION: Starting Generation {self.generation_id}")
        
        if not self.agents:
            print("[!] SWARM: Total Collapse! Resetting population.")
            for i in range(3):
                self.spawn_agent(f"genesis_{i}")
            return

        # 1. Selection
        self.cleanup_agents()
        self.enforce_diversity()

        # 2. Reproduction
        sorted_agents = sorted(self.agents.values(), key=lambda a: a.performance_score, reverse=True)
        if not sorted_agents: return

        # Top 20% can reproduce
        top_tier = sorted_agents[:max(1, len(sorted_agents)//5)]
        new_offspring = []
        
        for parent in top_tier:
            # Reproduce if they have enough balance
            if parent.economy.get_balance() >= self.spawn_cost:
                 parent.economy.spend(self.spawn_cost, "REPRODUCTION_COST")
                 
                 # Randomly decide asexual or sexual
                 if len(top_tier) > 1 and random.random() < 0.3:
                      partner = random.choice([a for a in top_tier if a != parent])
                      child = parent.reproduce(partner=partner)
                 else:
                      child = parent.reproduce()
                      
                 new_offspring.append(child)
                 print(f"[*] REPRODUCTION: {parent.agent_id[:8]} spawned {child.agent_id[:8]}")

        # Add offspring to population
        for child in new_offspring:
            child.state = AgentState.ACTIVE
            self.agents[child.agent_id] = child

        # Hard Cap on population
        if len(self.agents) > self.max_concurrent_agents:
             # Prune bottom agents to maintain cap
             prune_count = len(self.agents) - self.max_concurrent_agents
             sorted_all = sorted(self.agents.values(), key=lambda a: a.performance_score)
             for i in range(prune_count):
                  aid = sorted_all[i].agent_id
                  print(f"[*] POP_CAP: Removing agent {aid[:8]} to maintain limits.")
                  del self.agents[aid]
