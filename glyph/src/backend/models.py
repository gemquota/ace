import uuid
import networkx as nx
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional

class AgentPayload(BaseModel):
    model_config = ConfigDict(extra='allow') # Genesis Schema Override

    agent_id: str = Field(default_factory=lambda: f"agt_{uuid.uuid4().hex[:4]}")
    context_window: List[str] = []
    current_role: str = "Explorer"
    priority_score: float = 1.0
    entropy_index: float = 1.0
    lineage_hash: Optional[str] = None
    memory_refs: List[str] = []
    metadata: Dict = {}
    is_legacy: bool = False # Genesis Tag

class Node:
    def __init__(self, node_id, glyph, type_name):
        self.id = node_id
        self.glyph = glyph
        self.type = type_name
        self.links = []
        self.visits = 0 
        self.last_visited_tick = 0

GLYPHS = {
    '⟐': 'anchor', '⊢': 'emerge', '⊣': 'resolve', '⟳': 'loop', '⌁': 'trace',
    '◊': 'branch', '≠': 'divergence', '✳': 'spawn', '✂': 'delete', '⇄': 'rewire', '⌬': 'mutate',
    '(': 'scope_open', ')': 'scope_close',
    '⟡': 'transform', '∇': 'compress', '꩜': 'brainstorm', '⎋': 'critique',
    '⊕': 'commit', '≈': 'recall', '⇥': 'prune',
    '⧉': 'replicate', '⛖': 'sync', '☍': 'debate', '∿': 'broadcast',
    '☁': 'uplink', '🖧': 'localize'
}

class Graph:
    def __init__(self):
        self.nx_graph = nx.DiGraph()
        self.root = None
        self.node_data = {}

    def add_node(self, node_id, glyph):
        if not self.root: self.root = node_id
        type_name = GLYPHS.get(glyph, 'unknown')
        self.nx_graph.add_node(node_id, glyph=glyph, type=type_name)
        self.node_data[node_id] = {'id': node_id, 'glyph': glyph, 'type': type_name, 'links': [], 'visits': 0, 'last_visited_tick': 0}

    def add_edge(self, src, tgt):
        if src in self.nx_graph and tgt in self.nx_graph:
            self.nx_graph.add_edge(src, tgt)

    def is_fractured(self):
        if len(self.nx_graph.nodes) == 0: return False
        components = list(nx.weakly_connected_components(self.nx_graph))
        return len(components) > 1

    def serialize(self):
        nodes = []
        for nid in self.nx_graph.nodes:
            data = self.node_data[nid]
            data['links'] = list(self.nx_graph.successors(nid))
            nodes.append(data)
        return {'nodes': nodes, 'root': self.root}

    def load_serialized(self, data):
        self.nx_graph.clear()
        self.node_data.clear()
        self.root = data.get('root')
        for n in data.get('nodes', []):
            self.add_node(n['id'], n['glyph'])
        for n in data.get('nodes', []):
            for target in n.get('links', []):
                self.add_edge(n['id'], target)

def parse_gfs(text):
    graph = Graph()
    stack, last_node_id = [], None
    for char in text:
        if char in GLYPHS and char not in ['(', ')']:
            nid = str(uuid.uuid4())[:8]
            graph.add_node(nid, char)
            if stack: graph.add_edge(stack[-1], nid)
            elif last_node_id: graph.add_edge(last_node_id, nid)
            last_node_id = nid
        elif char == '(':
            if last_node_id: stack.append(last_node_id)
            last_node_id = None
        elif char == ')':
            if stack: last_node_id = stack.pop()
    return graph
