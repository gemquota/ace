import time
from typing import Optional, Dict, Any
from clide.kernel import syscalls, healer
from clide.types.event_types import Layer, EventType
from pie.engine import PieEngine
from pie.inference import PieInference
from clide.sovereign.engine import SovereignGoalEngine
from clide.meta.model import SelfArchitectureModel
from clide.meta.evaluator import ArchitectureEvaluator
from clide.meta.experiment import ExperimentFramework
from clide.swarm.manager import SwarmManager
from clide.kernel.router import TraceRouter

import threading

try:
    import psutil
except ImportError:
    psutil = None

class AutonomousLoop:
    def __init__(self, trace_id: str):
        from clide.kernel.orchestrator import CapOrchestrator
        self.trace_id = trace_id
        self.pie_engine = PieEngine()
        self.state = "OBSERVING"
        self.running = True
        self.sovereign = SovereignGoalEngine(trace_id=self.trace_id)
        self.orchestrator = CapOrchestrator(trace_id=self.trace_id)
        # Phase 20: Swarm & Economic Substrate
        self.swarm = SwarmManager()
        self.router = TraceRouter(master_trace_id=self.trace_id)
        # Phase 18: Meta-Cognition
        self.arch_model = SelfArchitectureModel.load()
        self.evaluator = ArchitectureEvaluator(self.arch_model)
        self.experimenter = ExperimentFramework(self.arch_model)
        self.cycle_count = 0
        
        # Phase 19: Hardware Polling
        self.hardware_state = {"cpu_percent": 0.0, "thermal_warning": False}
        self.polling_thread = threading.Thread(target=self._hardware_polling_loop, daemon=True)
        self.polling_thread.start()

    def _hardware_polling_loop(self):
        """10-second psutil CPU/Thermal polling loop."""
        while True:
            if psutil:
                cpu = psutil.cpu_percent(interval=1.0)
                self.hardware_state["cpu_percent"] = cpu
                
                # Simulated thermal check if sensors_temperatures not available
                temps = getattr(psutil, "sensors_temperatures", lambda: {})()
                thermal_warning = False
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current > 75.0: # Arbitrary threshold
                            thermal_warning = True
                
                self.hardware_state["thermal_warning"] = thermal_warning
                if cpu > 80.0 or thermal_warning:
                    print(f"  [!] HARDWARE WARNING: CPU={cpu}% Thermal={thermal_warning}")
                    import os
                    os.environ["CAP_SUBSTRATE_MIGRATE"] = "1"
                else:
                    import os
                    os.environ["CAP_SUBSTRATE_MIGRATE"] = "0"
            time.sleep(10)


    def run_cycle(self):
        self.cycle_count += 1
        print(f"[*] Autonomous Cycle: {self.state} (Cycle: {self.cycle_count})")
        
        # 0. Get parent for state update
        try:
            events = self.pie_engine.load_trace(self.trace_id)
        except ValueError:
            # Trace is corrupted, we might need a more advanced healer here
            # For now, let it crash to reveal the break
            raise

        if not events:
            # Handle empty/new trace by committing start
            print(f"[*] Initializing New Trace: {self.trace_id}")
            syscalls.cap_event_commit(
                trace_id=self.trace_id,
                layer=Layer.CAP,
                event_type=EventType.TRACE_START,
                payload={"initialized_by": "AutonomousLoop"},
                causal_parent=None
            )
            events = self.pie_engine.load_trace(self.trace_id)

        last_event_id = events[-1].event_id if events else None

        # 1. Update system state
        syscalls.cap_event_commit(
            trace_id=self.trace_id,
            layer=Layer.CAP,
            event_type=EventType.SYSTEM_STATE,
            payload={"state": self.state},
            causal_parent=last_event_id
        )
        
        # 2. Ingest + Infer
        events = self.pie_engine.load_trace(self.trace_id)
        inf = PieInference(events)
        inf_state = inf.analyze()
        
        # 3. Drift Detection (Autonomous Monitoring)
        drift_report = self._detect_drift(inf_state, events)
        if drift_report:
            print(f"  [!] DRIFT DETECTED: {drift_report['subsystem']} ({drift_report['severity']})")
            self.state = "RECOVERING"
            healer.heal_system(self.trace_id, drift_report)
            self.state = "OBSERVING"
        else:
            print("  [*] NO DRIFT. SYSTEM HEALTHY.")
            self.state = "IDLE"

            # 0. Refresh last_event_id for goal generation
            events = self.pie_engine.load_trace(self.trace_id)
            last_event_id = events[-1].event_id if events else last_event_id

            # Phase 17: Sovereign Intent Generation
            new_goals = self.sovereign.generate_goals(inf_state, causal_parent=last_event_id)
            
            # Phase 18: Meta-Cognitive Evolution
            if self.cycle_count % 5 == 0:
                print("  [*] META: Evaluating Architecture...")
                # Update metrics from current trace
                self.arch_model.update_metrics("PIE", {"success_rate": inf_state.execution_summary.get("success_rate", 1.0)})
                self.arch_model.update_metrics("APC", {"efficiency": inf_state.execution_summary.get("success_rate", 1.0)})
                
                proposals = self.evaluator.evaluate()
                for p in proposals:
                    self.experimenter.run_experiment(p)
                
                # Meta-goals
                meta_goals = self.evaluator.get_meta_goals()
                for mg in meta_goals:
                    from clide.sovereign.engine import Goal
                    import heapq
                    heapq.heappush(self.sovereign.goal_queue, Goal(**mg, priority=0.8, utility=0.9))

            if new_goals:
                print(f"  [*] SOVEREIGN: Generated {len(new_goals)} goals.")
                # Refresh for selection
                events = self.pie_engine.load_trace(self.trace_id)
                last_event_id = events[-1].event_id if events else last_event_id
            
            next_goal = self.sovereign.select_next_goal(causal_parent=last_event_id)
            if next_goal:
                print(f"  [*] SOVEREIGN: Executing Autonomous Goal: {next_goal.goal} ({next_goal.reason})")
                self.state = "EXECUTING_SWARM"
                
                # Phase 20: Multi-Agent Parallel Execution
                agent_names = ["speed_demon", "conservative_guard", "balanced_worker"]
                agent_ids = [self.swarm.spawn_agent(name) for name in agent_names]
                
                agent_traces = []
                from clide.kernel.orchestrator import CapOrchestrator
                from clide.kernel.planner import StrategyMode

                for aid in agent_ids:
                    # Spawn a branch for each agent
                    child_trace = syscalls.spawn_agent_trace(self.trace_id, aid)
                    
                    # Choose strategy based on agent name
                    mode = StrategyMode.ADAPTIVE
                    if "speed" in self.swarm.agents[aid].name:
                        mode = StrategyMode.CONSERVATIVE # Actually speed might be AGGRESSIVE if we had it
                    elif "conservative" in self.swarm.agents[aid].name:
                        mode = StrategyMode.CONSERVATIVE
                    
                    print(f"    [*] SWARM: Dispatching Agent {aid[:8]} ({self.swarm.agents[aid].name}) on trace {child_trace}")
                    child_orchestrator = CapOrchestrator(trace_id=child_trace, agent_id=aid)
                    res = child_orchestrator.execute_goal(next_goal.goal, mode=mode, max_cycles=5)
                    
                    if res:
                        success_rate = res.execution_summary.get("success_rate", 0.0)
                        # Estimate credit cost (this should ideally come from child_orchestrator.economy)
                        cost = child_orchestrator.economy.get_balance() # Balance spent
                        
                        agent_traces.append({
                            "trace_id": child_trace,
                            "agent_id": aid,
                            "success_rate": success_rate,
                            "credit_cost": 100.0 - cost # Amount spent
                        })
                        
                        # Update agent performance
                        self.swarm.agents[aid].update_performance(success_rate, 1.0)

                # Refresh last_event_id for merge commitment
                events = self.pie_engine.load_trace(self.trace_id)
                last_event_id = events[-1].event_id if events else last_event_id

                # Merge the best trace back to master
                winner = self.router.merge_best_trace(agent_traces, causal_parent=last_event_id)
                if winner:
                    print(f"    [*] SWARM: Winner selected: Agent {winner['agent_id'][:8]} (Success: {winner['success_rate']*100}%)")
                
                # Evolutionary Pressure
                self.swarm.trigger_evolution()
                self.state = "OBSERVING"
                # Save model
                self.arch_model.save()
            
    def _detect_drift(self, inf_state, events) -> Optional[Dict[str, Any]]:
        # Heuristic 1: Cluster of failures
        if "REPEATED_FAILURE_CLUSTER" in inf_state.anomaly_flags:
            # Find last good event before the failure cluster
            last_good = None
            for e in events:
                if e.event_type.value == "EXEC_COMPLETE":
                    if e.payload.get("exit_code") == 0:
                        last_good = e.event_id
                    else:
                        break
            
            return {
                "severity": "HIGH",
                "subsystem": "APC",
                "reason": "FAILURE_CLUSTER",
                "last_good_event": last_good
            }
        
        # Heuristic 2: Low success rate
        if inf_state.execution_summary.get("success_rate", 1.0) < 0.5:
             return {
                "severity": "MEDIUM",
                "subsystem": "APC",
                "reason": "LOW_SUCCESS_RATE"
            }
             
        return None

    def start(self, interval=5):
        print(f"[*] Starting Autonomous Loop for trace {self.trace_id}")
        try:
            while self.running:
                self.run_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        self.running = False
        print("[*] Autonomous Loop Stopped.")
