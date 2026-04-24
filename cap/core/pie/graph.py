import networkx as nx
from typing import List, Dict, Any
from clide.kernel.events import Event
from clide.types.event_types import EventType, Layer

class TraceGraph:
    def __init__(self, events: List[Event]):
        self.events = events
        self.g_event = nx.DiGraph()
        self.g_causal = nx.DiGraph()
        self.g_entity = nx.Graph()
        self._build_graphs()

    def _build_graphs(self):
        last_exec_cmd = None
        for i, ev in enumerate(self.events):
            # ... existing logic ...
            self.g_event.add_node(ev.event_id, type="event", event_type=ev.event_type.value)
            if i > 0:
                self.g_event.add_edge(self.events[i-1].event_id, ev.event_id, type="temporal")

            if ev.causal_parent:
                self.g_causal.add_edge(ev.causal_parent, ev.event_id, type="causal")

            if ev.event_type == EventType.EXEC_SPAWN:
                cmd = ev.payload.get("command", "")
                cmd_base = cmd.split()[0] if cmd else "unknown"
                self.g_entity.add_node(ev.event_id, type="command", command=cmd)
                
                if last_exec_cmd:
                    edge = (last_exec_cmd, cmd_base)
                    if self.g_causal.has_edge(*edge):
                        self.g_causal[edge[0]][edge[1]]["weight"] += 1
                    else:
                        self.g_causal.add_edge(*edge, type="command_transition", weight=1)
                last_exec_cmd = cmd_base

            if ev.event_type == EventType.EXEC_COMPLETE:
                se_hash = ev.payload.get("side_effect_hash")
                if se_hash:
                    self.g_entity.add_node(se_hash, type="state_change")
                    self.g_entity.add_edge(ev.causal_parent, se_hash, type="affects")

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.g_event.number_of_nodes(),
            "total_edges": self.g_event.number_of_edges(),
            "causal_depth": nx.dag_longest_path_length(self.g_causal) if self.g_causal.number_of_nodes() > 0 else 0
        }
