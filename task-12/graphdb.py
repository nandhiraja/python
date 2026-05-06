import cmd
import time
from parser import QueryParser
from engine import GraphEngine

class GraphDBShell(cmd.Cmd):
    intro = '=== Graph DB Shell ===\nType your query or help or exit.'
    prompt = 'graphdb> '

    def __init__(self):
        super().__init__()
        self.engine = GraphEngine("graph.wal")
        self.parser = QueryParser()
        self.aliases = {} 
        self.multiline_buffer = ""

    def precmd(self, line):
        return line

    def default(self, line):
        if not line:
            return

        if self.multiline_buffer:
            self.multiline_buffer += " " + line
        else:
            self.multiline_buffer = line

        if self.multiline_buffer.upper().startswith("MATCH") and "RETURN" not in self.multiline_buffer.upper():
            return
            
        query = self.multiline_buffer
        self.multiline_buffer = ""

        try:
            parsed = self.parser.parse(query)
            if not parsed:
                print("Error: Syntax error or unsupported query.")
                return

            if parsed["type"] == "CREATE_NODE":
                node = self.engine.create_node(parsed["label"], parsed["properties"])
                if parsed["alias"]:
                    self.aliases[parsed["alias"]] = node.node_id
                print(f"Node created: {node.label}#{node.node_id}")

            elif parsed["type"] == "CREATE_EDGE":
                src_alias = parsed["source_alias"]
                tgt_alias = parsed["target_alias"]
                
                src_id = self.aliases.get(src_alias)
                tgt_id = self.aliases.get(tgt_alias)
                
                if src_id is None or tgt_id is None:
                    print(f"Error: Could not resolve aliases {src_alias} or {tgt_alias}")
                    return
                    
                edge = self.engine.create_edge(src_id, tgt_id, parsed["edge_type"], parsed["properties"])
                print(f"Edge created: Node#{src_id} —{edge.type}-> Node#{tgt_id}")

            elif parsed["type"] == "MATCH":
                start_time = time.time()
                rows, stats = self.engine.match(parsed["nodes"], parsed["edges"], parsed["conditions"], parsed["returns"])
                elapsed_ms = (time.time() - start_time) * 1000
                
                if not rows:
                    print("0 rows returned.")
                    return
                    
                headers = [f"{a}.{p}" for a, p in parsed["returns"]]
                
                col_widths = [len(h) for h in headers]
                for row in rows:
                    for i, val in enumerate(row):
                        col_widths[i] = max(col_widths[i], len(str(val)))
                
                separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
                
                print(separator)
                header_str = "|" + "|".join(f" {h:<{w}} " for h, w in zip(headers, col_widths)) + "|"
                print(header_str)
                print(separator)
                
                for row in rows:
                    row_str = "|" + "|".join(f" {str(v):<{w}} " for v, w in zip(row, col_widths)) + "|"
                    print(row_str)
                    
                print(separator)
                print(f"{len(rows)} row returned (traversal: {stats['nodes_traversed']} nodes, {stats['edges_traversed']} edges) in {elapsed_ms:.1f}ms")

            elif parsed["type"] == "SHORTEST_PATH":
                src_alias = parsed["source_alias"]
                tgt_alias = parsed["target_alias"]
                
                src_id = self.aliases.get(src_alias)
                tgt_id = self.aliases.get(tgt_alias)
                
                if src_id is None or tgt_id is None:
                    print(f"Error: Could not resolve aliases {src_alias} or {tgt_alias}")
                    return
                    
                path, total_weight = self.engine.shortest_path(src_id, tgt_id, parsed["min_hops"], parsed["max_hops"])
                
                if path:
                    path_str = ""
                    for i, item in enumerate(path):
                        if i % 2 == 0:
                            path_str += item.properties.get("name", f"{item.label}#{item.node_id}")
                        else:
                            path_str += f" —{item.type}-> "
                            
                    print(f"Path: {path_str}")
                    print(f"Length: {len(path)//2} hops | Total weight: {total_weight}")
                else:
                    print("No path found.")

            elif parsed["type"] == "STATS":
                stats = self.engine.get_stats()
                idx_str = f"{stats['indexes']} ({', '.join(stats['index_keys'])})" if stats['indexes'] > 0 else "0"
                print(f"Nodes: {stats['nodes']} | Edges: {stats['edges']} | Indexes: {idx_str}")
                print(f"WAL: {stats['wal_entries']} entries | Uptime: {stats['uptime_sec']} sec")

        except Exception as e:
            print(f"Execution error: {e}")

    def do_exit(self, arg):
        """Exit the shell."""
        print('Bye')
        return True

    def do_EOF(self, arg):
        """Exit the shell."""
        print('Bye')
        return True

if __name__ == '__main__':
    GraphDBShell().cmdloop()
