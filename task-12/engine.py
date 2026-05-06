import heapq
import time
from collections import defaultdict
from models import Node, Edge
from wal import WALManager

class GraphEngine:
    def __init__(self, wal_path="graph.wal"):
        self.nodes = {}
        self.edges = {}
        self.adj_out = defaultdict(list)
        self.adj_in = defaultdict(list)
        # index: (label, property_key) -> property_value -> set of node_ids
        self.indices = defaultdict(lambda: defaultdict(set))
        self.wal = WALManager(wal_path)
        self.next_node_id = 1
        self.next_edge_id = 1
        
        self.start_time = time.time()
        self._recover()

    def _recover(self):
        mutations = self.wal.recover()
        for mut in mutations:
            m_type = mut["mutation"]
            data = mut["data"]
            if m_type == "CREATE_NODE":
                node = Node.from_dict(data)
                self._add_node_internal(node)
                self.next_node_id = max(self.next_node_id, node.node_id + 1)
            elif m_type == "CREATE_EDGE":
                edge = Edge.from_dict(data)
                self._add_edge_internal(edge)
                self.next_edge_id = max(self.next_edge_id, edge.edge_id + 1)

    def _update_index(self, node: Node):
        for key, value in node.properties.items():
            self.indices[(node.label, key)][value].add(node.node_id)

    def _add_node_internal(self, node: Node):
        self.nodes[node.node_id] = node
        self._update_index(node)

    def _add_edge_internal(self, edge: Edge):
        self.edges[edge.edge_id] = edge
        self.adj_out[edge.source_id].append(edge)
        self.adj_in[edge.target_id].append(edge)

    def create_node(self, label, properties):
        node = Node(self.next_node_id, label, properties)
        self.next_node_id += 1
        self._add_node_internal(node)
        self.wal.append_mutation("CREATE_NODE", node.to_dict())
        return node

    def create_edge(self, source_id, target_id, edge_type, properties):
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node does not exist")
        edge = Edge(self.next_edge_id, source_id, target_id, edge_type, properties)
        self.next_edge_id += 1
        self._add_edge_internal(edge)
        self.wal.append_mutation("CREATE_EDGE", edge.to_dict())
        return edge

    def get_stats(self):
        num_indices = len(self.indices)
        wal_size = self.wal.get_size()
        uptime = int(time.time() - self.start_time)
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "indexes": num_indices,
            "index_keys": [f"{l}.{k}" for l, k in self.indices.keys()],
            "wal_entries": wal_size,
            "uptime_sec": uptime
        }

    def shortest_path(self, source_id, target_id, min_hops=1, max_hops=4, weight_property="weight"):
        if source_id not in self.nodes or target_id not in self.nodes:
            return None, 0
            
        pq = [(0, source_id, [source_id])]
        visited = {} 
        visited[(source_id, 0)] = 0

        best_path = None
        best_weight = float('inf')

        while pq:
            weight, curr_id, path = heapq.heappop(pq)
            hops = len(path) // 2

            if curr_id == target_id and hops >= min_hops and hops <= max_hops:
                if weight < best_weight:
                    best_weight = weight
                    best_path = path
                continue
                
            if hops >= max_hops:
                continue

            for edge in self.adj_out[curr_id]:
                next_id = edge.target_id
                edge_weight = float(edge.properties.get(weight_property, 1.0))
                new_weight = weight + edge_weight
                new_hops = hops + 1
                
                if new_weight < visited.get((next_id, new_hops), float('inf')):
                    visited[(next_id, new_hops)] = new_weight
                    heapq.heappush(pq, (new_weight, next_id, path + [edge.edge_id, next_id]))

        if best_path:
            result_path = []
            for i, item_id in enumerate(best_path):
                if i % 2 == 0:
                    result_path.append(self.nodes[item_id])
                else:
                    result_path.append(self.edges[item_id])
            return result_path, best_weight
        return None, 0

    def match(self, pattern_nodes, pattern_edges, conditions, returns):
        results = []
        
        def node_matches(node, pat_node):
            if pat_node.get('label') and node.label != pat_node['label']:
                return False
            for k, v in pat_node.get('properties', {}).items():
                if node.properties.get(k) != v:
                    return False
            return True

        def edge_matches(edge, pat_edge):
            if pat_edge.get('type') and edge.type != pat_edge['type']:
                return False
            return True

        def eval_conditions(env):
            for alias, key, op, val in conditions:
                obj = env.get(alias)
                if not obj:
                    return False
                obj_val = obj.properties.get(key)
                if op == '=' and obj_val != val:
                    return False
            return True

        start_pat = pattern_nodes[0]
        start_nodes = []
        
        indexed_nodes = None
        for alias, key, op, val in conditions:
            if alias == start_pat.get('alias') and op == '=' and start_pat.get('label'):
                if val in self.indices[(start_pat['label'], key)]:
                    indexed_nodes = self.indices[(start_pat['label'], key)][val]
                    break
        
        if indexed_nodes is not None:
            start_nodes = [self.nodes[nid] for nid in indexed_nodes if node_matches(self.nodes[nid], start_pat)]
        else:
            start_nodes = [n for n in self.nodes.values() if node_matches(n, start_pat)]

        def search(curr_node, depth, env):
            if depth == len(pattern_edges):
                if eval_conditions(env):
                    results.append(env)
                return

            pat_edge = pattern_edges[depth]
            next_pat_node = pattern_nodes[depth + 1]

            for edge in self.adj_out[curr_node.node_id]:
                if edge_matches(edge, pat_edge):
                    next_node = self.nodes[edge.target_id]
                    if node_matches(next_node, next_pat_node):
                        new_env = env.copy()
                        if pat_edge.get('alias'):
                            new_env[pat_edge['alias']] = edge
                        if next_pat_node.get('alias'):
                            new_env[next_pat_node['alias']] = next_node
                        
                        search(next_node, depth + 1, new_env)

        for sn in start_nodes:
            env = {}
            if start_pat.get('alias'):
                env[start_pat['alias']] = sn
            search(sn, 0, env)

        rows = []
        for env in results:
            row = []
            for alias, prop in returns:
                if alias in env:
                    row.append(env[alias].properties.get(prop, "NULL"))
                else:
                    row.append("NULL")
            rows.append(row)

        stats = {
            "nodes_traversed": len(pattern_nodes),
            "edges_traversed": len(pattern_edges)
        }
            
        return rows, stats
