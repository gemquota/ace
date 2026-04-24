import os
import time
import concurrent.futures
from typing import List, Dict, Any, Optional
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from clide.compiler import IntentCompiler
from clide.kernel.scheduler import DAGScheduler, NodeStatus
from clide.kernel.planner import OrchestrationState, PlanMutationEngine, StrategyMode
from clide.state_graph import CognitiveStateGraph, NodeType, CognitiveNode
from apc import executor
from pie.engine import PieEngine
from pie.inference import PieInference, InferenceState
from clide.memory.store import MemoryStore
from clide.memory.retrieval import HybridRetriever
from clide.memory.working_memory import WorkingMemory
from clide.memory.episodic_index import EpisodicIndex, Episode
from clide.memory.semantic_store import SemanticStore
from clide.memory.episode_builder import EpisodeBuilder
from clide.memory.consolidation import ConsolidationProcess
...
class CapOrchestrator:
    def __init__(self, trace_id: Optional[str] = None, agent_id: str = "prime"):
        self.trace_id = trace_id or syscalls.cap_trace_start()
        self.agent_id = agent_id
        self.compiler = IntentCompiler(trace_id=self.trace_id)
        self.pie_engine = PieEngine()
        self.last_inference: Optional[InferenceState] = None
        self.memory_store = MemoryStore()
        self.working_memory = WorkingMemory(trace_id=self.trace_id)
        self.episodic_index = EpisodicIndex()
        self.semantic_store = SemanticStore()
        self.retriever = HybridRetriever(
            self.memory_store, 
            working_memory=self.working_memory,
            semantic_store=self.semantic_store,
            episodic_index=self.episodic_index
        )
        self.episode_builder = EpisodeBuilder(trace_id=self.trace_id)
        self.consolidation = ConsolidationProcess(self.episodic_index, self.semantic_store)
        self.state_graph = CognitiveStateGraph(trace_id=self.trace_id)
        self.rollback_horizon_hours = 4.0
        from clide.swarm.economy import ComputeCredit
        self.economy = ComputeCredit(agent_id=self.agent_id)
        self.remote_tunnel = None
        
    def _evaluate_compute_weight(self, goal: str, dag) -> bool:
        """Evaluate if an intent is high-load and should be routed remotely."""
        high_load_keywords = ["compile", "build", "train model", "analyze deep", "stress_test"]
        is_high_load = any(k in goal.lower() for k in high_load_keywords)
        
        # Substrate migration trigger from loop hardware polling
        substrate_migrate = os.environ.get("CAP_SUBSTRATE_MIGRATE") == "1"
        
        return is_high_load or substrate_migrate


    def check_temporal_horizon(self, events: List[Dict[str, Any]]) -> bool:
        """Check if the current trace extends beyond the 4-hour temporal horizon.
        Uses Lamport ticks conceptually bounded by wall-clock time mapping.
        """
        if not events:
            return True
        first_event_time = events[0].get("timestamp", time.time())
        current_time = time.time()
        elapsed_hours = (current_time - first_event_time) / 3600.0
        if elapsed_hours > self.rollback_horizon_hours:
            print(f"[!] TEMPORAL HORIZON BREACHED: {elapsed_hours:.2f} hours elapsed. Initiating Rollback.")
            return False
        return True

    def execute_goal(self, goal: str, mode: StrategyMode = StrategyMode.ADAPTIVE, max_cycles: int = 20, use_queue: bool = False):
        print(f"[*] GOAL: {goal}")
        
        # Phase 20: Unified Cognitive State Graph
        goal_node = CognitiveNode(
            type=NodeType.GOAL,
            content=goal,
            metadata={"status": "ACTIVE", "mode": mode.value},
            agent_id=self.agent_id,
            trace_id=self.trace_id
        )
        self.state_graph.add_node(goal_node)

        # 0. Get parent for intent
        from clide.storage import db
        events = db.get_events_by_trace(self.trace_id)
        last_event_id = events[-1]["event_id"] if events else None

        if not self.check_temporal_horizon(events):
            print("[!] Halting execution due to temporal horizon breach.")
            goal_node.metadata["status"] = "FAILED"
            goal_node.metadata["reason"] = "TEMPORAL_HORIZON_BREACH"
            return None

        # 1. Initial Compilation
        if self.last_inference:
            self.compiler.inject_context(self.last_inference)
        
        dag = self.compiler.compile(goal, causal_parent=last_event_id)
        print(f"[*] INITIAL PLAN: {len(dag.actions)} actions (Intent: {dag.intent_id[:8]}...)")
        
        # Record Plan in State Graph
        plan_node = CognitiveNode(
            type=NodeType.PLAN,
            content=dag.to_dict(),
            agent_id=self.agent_id,
            trace_id=self.trace_id
        )
        self.state_graph.add_node(plan_node)
        self.state_graph.add_edge(plan_node.id, goal_node.id, edge_type="SUPPORTS")

        # 2. Setup Orchestration State & Planner
        events = db.get_events_by_trace(self.trace_id)
        intent_event_id = events[-1]["event_id"] if events else None
        
        state = OrchestrationState(trace_id=self.trace_id, dag=dag, strategy=mode, state_graph=self.state_graph)
        planner = PlanMutationEngine(state)
        scheduler = DAGScheduler(trace_id=self.trace_id, dag=dag, use_queue=use_queue)
        
        # 3. Dynamic Execution Loop
        running_futures = {} # Future -> ActionNode
        cycles = 0
        
        use_remote = self._evaluate_compute_weight(goal, dag) and self.remote_tunnel is not None
        if use_remote:
            print("[*] SUBSTRATE MIGRATION TRIGGERED: Routing execution to remote tunnel.")

        while not scheduler.is_complete() and cycles < max_cycles:
            cycles += 1
            # A. Dispatch next actions
            ready = scheduler.get_ready_nodes()
            for node in ready:
                if node.action_id not in [n.action_id for n in running_futures.values()]:
                    # Record Action in State Graph
                    action_node = CognitiveNode(
                        type=NodeType.ACTION,
                        content={"command": node.command},
                        agent_id=self.agent_id,
                        trace_id=self.trace_id
                    )
                    self.state_graph.add_node(action_node)
                    self.state_graph.add_edge(action_node.id, plan_node.id, edge_type="PART_OF")

                    if use_remote:
                        print(f"[*] DISPATCHING REMOTE: {node.command}")
                        # Filter context window for remote agent
                        context = self.state_graph.get_context_window(self.agent_id)
                        
                        # Execute synchronously for remote (simplified wrapper, should be async ideally)
                        # We pass context but remote_tunnel.execute_remote might need to be updated to handle it.
                        res = self.remote_tunnel.execute_remote(node.command)
                        
                        # Cache the remote event
                        self.remote_tunnel.cache.cache_event({
                            "event_type": "REMOTE_EXEC",
                            "trace_id": self.trace_id,
                            "command": node.command,
                            "stdout": res["stdout"],
                            "stderr": res["stderr"],
                            "exit_code": res["exit_code"],
                            "timestamp": time.time(),
                            "context_snapshot": context
                        })
                        
                        # Mock a future for the scheduler to consume
                        future = concurrent.futures.Future()
                        future.set_result(res)
                        running_futures[future] = node
                    else:
                        print(f"[*] DISPATCHING: {node.command} (via {'Queue' if use_queue else 'Local'})")
                        future = scheduler.execute_async(node, intent_event_id)
                        running_futures[future] = node

            
            if not running_futures:
                if scheduler.is_complete(): break
                time.sleep(0.1)
                continue

            # B. Wait for any action to complete
            done, not_done = concurrent.futures.wait(
                running_futures.keys(), 
                timeout=30.0,
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                node = running_futures.pop(future)
                res = future.result()
                print(f"[*] COMPLETED: {node.command} (Code: {res['exit_code']})")
                
                # Phase 20: Commit Fact of outcome
                self.state_graph.commit_fact(
                    content={"action_id": node.action_id, "exit_code": res["exit_code"]},
                    metadata={"stdout": res.get("stdout", ""), "stderr": res.get("stderr", "")}
                )

                # Phase 20: Deduct credits
                # Calculate cost based on duration
                cost = self.economy.calculate_cost(cpu_time=0.0, duration=res.get("duration_ms", 0) / 1000.0)
                if not self.economy.spend(cost, f"EXEC:{node.command[:20]}"):
                    print(f"[!] BANKRUPTCY: Agent {self.agent_id} cannot afford further execution.")
                    scheduler.stop_execution = True
                    break
                
                # C. Incremental PIE Inference
                trace_events = self.pie_engine.load_trace(self.trace_id)
                self.last_inference = PieInference(trace_events).analyze()
                state.inferred_state = self.last_inference
                
                # Phase 20: Record Inference in State Graph
                inf_node = CognitiveNode(
                    type=NodeType.INFERENCE,
                    content=self.last_inference.execution_summary,
                    confidence=self.last_inference.execution_summary.get("success_rate", 1.0),
                    agent_id="pie_inference_engine",
                    trace_id=self.trace_id
                )
                self.state_graph.add_node(inf_node)

                # D. Evaluate State & Adjust Plan
                if res["exit_code"] != 0:
                    print(f"[!] FAILURE DETECTED in {node.command}")
                    
                    if state.strategy == StrategyMode.CONSERVATIVE:
                        print("[!] CONSERVATIVE MODE: Halting on failure.")
                        scheduler.stop_execution = True
                        goal_node.metadata["status"] = "FAILED"
                        break
                        
                    # Suggest corrections
                    corrections = planner.suggest_corrections(node, self.last_inference)
                    if corrections:
                        print(f"[*] PLAN MUTATION: Inserting {len(corrections)} corrective actions.")
                        for corr in corrections:
                            planner.insert_node(corr, before_node_id=node.action_id)
                            # Reset node status so it can be retried after corrections
                            scheduler.status[node.action_id] = NodeStatus.PENDING
                        
                        scheduler.update_dag(state.dag)
                    else:
                        print(f"[*] No corrections found for {node.command}")
                
                # E. Adaptive Strategy Switching
                if state.strategy == StrategyMode.ADAPTIVE:
                    success_rate = self.last_inference.execution_summary.get("success_rate", 1.0)
                    if success_rate < 0.5:
                        print("[*] ADAPTIVE: Low success rate. Switching to CONSERVATIVE.")
                        planner.update_strategy(StrategyMode.CONSERVATIVE)

        scheduler.shutdown()
        if cycles >= max_cycles:
            print(f"[!] ORCHESTRATION LIMIT REACHED ({max_cycles} cycles).")
            goal_node.metadata["status"] = "FAILED"
        
        if self.last_inference:
            print(f"[*] GOAL COMPLETE: Success Rate: {self.last_inference.execution_summary['success_rate'] * 100}%")
            if self.last_inference.execution_summary['success_rate'] == 1.0:
                 goal_node.metadata["status"] = "COMPLETED"
            else:
                 goal_node.metadata["status"] = "PARTIAL_SUCCESS"

            # Phase 20: Persistent Cognitive Memory storage
            outcome = "success" if self.last_inference.execution_summary["success_rate"] == 1.0 else "failure"
            primitive = dag.metadata.get("primitive", "default")
            commands = [a.command for a in dag.actions]
            self.memory_store.store_sequence(
                intent_label=primitive,
                commands=commands,
                outcome=outcome,
                trace_id=self.trace_id,
                metadata={"total_cycles": cycles, "goal": goal}
            )

            # Phase 20: Memory System Evolution (Episodic + Semantic)
            episode = self.episode_builder.build_from_raw_events(trace_events)
            if episode:
                 self.episodic_index.add_episode(episode)
                 print(f"[*] Episodic Memory: Stored episode {episode.episode_id[:8]} for goal: {goal}")
                 
                 # Run consolidation cycle (could be backgrounded, but for now we'll do it here)
                 self.consolidation.run_consolidation_cycle()

            # Adjust pattern weights
            delta = 0.1 if outcome == "success" else -0.1
            import hashlib
            for cmd in commands:
                cmd_hash = hashlib.sha256(cmd.encode()).hexdigest()
                self.memory_store.update_pattern_weight(cmd_hash, "n-gram", delta)

        return self.last_inference

    def shutdown(self):
        from clide.storage import db
        # Phase 16: Periodic pruning of memory
        self.memory_store.prune_stale_patterns()

        events = db.get_events_by_trace(self.trace_id)
        if events:
            syscalls.cap_trace_end(self.trace_id, events[-1]["event_id"])
        print(f"[*] TRACE {self.trace_id} CLOSED.")
