class TopologySubstrate:
    def __init__(self, graph, random_gen):
        self.graph = graph
        self.random = random_gen

    def garbage_collect(self, current_tick):
        to_remove = []
        for nid in list(self.graph.nx_graph.nodes):
            if nid == self.graph.root: continue
            last_visit = self.graph.node_data[nid]['last_visited_tick']
            if current_tick - last_visit > 150:
                to_remove.append(nid)
        
        for nid in to_remove:
            self.graph.nx_graph.remove_node(nid)
            del self.graph.node_data[nid]
        return to_remove

    def mutate_delete(self, node_id):
        nodes = list(self.graph.nx_graph.nodes)
        if len(nodes) > 1:
            target = self.random.choice(nodes)
            if target != self.graph.root and target != node_id:
                self.graph.nx_graph.remove_node(target)
                if self.graph.is_fractured():
                    self.graph.nx_graph.add_node(target) # Rollback
                    return None
                else:
                    del self.graph.node_data[target]
                    return target
        return None
