import random
import asyncio
from .models import GLYPHS, Node, AgentPayload
from .substrates import CognitiveSubstrate, MemorySubstrate, TelemetrySubstrate, TopologySubstrate

class Engine:
    def __init__(self, graph, seed=42, broadcast_queue=None):
        self.graph = graph
        self.seed = seed
        self.random = random.Random(seed)
        self.broadcast_queue = broadcast_queue
        
        self.events = []
        self.state = {'tick': 0, 'version': 'GFS-III'}
        
        # Initialize Substrates
        self.cognitive = CognitiveSubstrate(self)
        self.memory = MemorySubstrate(seed)
        self.telemetry = TelemetrySubstrate(broadcast_queue)
        self.topology = TopologySubstrate(graph, self.random)

        self.active_nodes = [(graph.root, self.create_genesis_payload())] if graph.root else []

    def create_genesis_payload(self):
        return AgentPayload(
            current_role="Explorer",
            entropy_index=1.0,
            priority_score=1.0
        )

    def _genesis_migration(self):
        # Scan payloads for Pydantic 'extra' fields caused by a rollback
        for i, (nid, payload) in enumerate(self.active_nodes):
            if payload.model_extra:
                # 1. Dump to Quarantine Table
                self.telemetry.quarantine(self.state['tick'], payload.agent_id, payload.model_extra)
                # 2. Tag as Legacy
                payload.is_legacy = True
                # 3. Strip extra fields
                payload.__pydantic_extra__ = None

    def step(self):
        self.state['tick'] += 1
        next_active = []
        
        # Genesis Validation Pre-Step
        self._genesis_migration()

        removed = self.topology.garbage_collect(self.state['tick'])
        for nid in removed:
            self.events.append({"type": "sys_gc", "node": nid})
        
        for node_id, payload in self.active_nodes:
            if node_id not in self.graph.nx_graph: continue
            
            # Entropy Kill-Switch Check
            if payload.entropy_index > 5.0:
                 self.events.append({"type": "kill_switch", "desc": f"Agent {payload.agent_id} terminated due to high entropy ({payload.entropy_index})."})
                 continue # Skip execution and propagation
                 
            # Update Node Metadata
            self.graph.node_data[node_id]['visits'] += 1
            self.graph.node_data[node_id]['last_visited_tick'] = self.state['tick']
            
            # Telemetry
            self.telemetry.record(self.state['tick'], payload)

            # Execution
            processed_payloads = self.execute_node(node_id, payload)
            
            # Propagation
            successors = list(self.graph.nx_graph.successors(node_id))
            for target_id in successors:
                for p in processed_payloads:
                    next_active.append((target_id, p.model_copy(deep=True)))

        self.active_nodes = next_active
        if not self.active_nodes and self.graph.root:
            self.events.append({"type": "fallback", "desc": "Graph starved. Re-anchoring."})
            self.active_nodes = [(self.graph.root, self.create_genesis_payload())]

    def execute_node(self, node_id, payload: AgentPayload):
        g = self.graph.node_data[node_id]['glyph']
        out = [payload]
        self.events.append({"type": GLYPHS.get(g, 'exec'), "node": node_id, "glyph": g})
        
        # GFS-III Execution Logic (Delegated to Substrates)
        if g == '⟡': # Transform
            text = " ".join(payload.context_window[-2:])
            res = self.cognitive.call([{"role": "user", "content": f"Advance: {text}"}], tier=1, role=payload.current_role)
            payload.context_window.append(res)
            
        elif g == '⎋': # Critique
            payload.current_role = "Critic"
            payload.entropy_index = 0.1
            text = " ".join(payload.context_window[-3:])
            res = self.cognitive.call([{"role": "user", "content": f"Critique logically: {text}"}], tier=2, role=payload.current_role)
            payload.context_window.append(f"[CRITIQUE]: {res}")

        elif g == '∇': # Compress
            payload.current_role = "Synthesizer"
            text = " ".join(payload.context_window)
            res = self.cognitive.call([{"role": "user", "content": f"Compress to directive: {text}"}], tier=2, role=payload.current_role)
            payload.context_window = [f"[SYNTHESIS]: {res}"]

        elif g == '≈': # Recall
            if payload.context_window:
                res = self.memory.query(payload.context_window[-1])
                if res:
                    payload.context_window.append(f"[RECALLED]: {res}")

        elif g == '⊕': # Commit
            text = " ".join(payload.context_window)
            if text:
                self.memory.store(text, payload.agent_id, self.state['tick'], payload.priority_score)

        elif g == '✂': # Delete (Mutation)
            target = self.topology.mutate_delete(node_id)
            if target:
                self.events.append({"type": "mutation", "desc": f"Pruned node {target}"})

        elif g == '꩜': # Brainstorm/Execute (JIT Compiler)
            self.cognitive.jit.compile_and_run(payload, self.graph)

        return out

    def get_state(self):
        active_edges = []
        for nid, p in self.active_nodes:
             successors = list(self.graph.nx_graph.successors(nid))
             for s in successors:
                 active_edges.append((nid, s))

        return {
            "graph": self.graph.serialize(),
            "active_nodes": [nid for nid, p in self.active_nodes],
            "active_edges": active_edges,
            "payloads": {nid: p.model_dump() for nid, p in self.active_nodes},
            "events": self.events[-30:],
            "state": self.state
        }
