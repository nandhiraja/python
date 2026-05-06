import re
import ast

class QueryParser:
    def __init__(self):
        pass

    def parse_properties(self, props_str):
        if not props_str:
            return {}
        props_str = re.sub(r'([a-zA-Z_]+)\s*:', r'"\1":', props_str)
        try:
            return ast.literal_eval(props_str)
        except:
            return {}

    def parse_create_node(self, query):
        match = re.match(r'CREATE\s+NODE\s+\((.*?)\)', query, re.IGNORECASE)
        if match:
            inner = match.group(1).strip()
            parts = inner.split('{', 1)
            alias_label = parts[0].strip()
            props_str = '{' + parts[1] if len(parts) > 1 else ''
            
            alias, label = alias_label.split(':', 1) if ':' in alias_label else (alias_label, '')
            props = self.parse_properties(props_str)
            return {
                "type": "CREATE_NODE",
                "alias": alias.strip(),
                "label": label.strip(),
                "properties": props
            }
        return None

    def parse_create_edge(self, query):
        match = re.match(r'CREATE\s+EDGE\s+\((.*?)\)-\[:(.*?)\s*(?:\{(.*?)\})?\]->\((.*?)\)', query, re.IGNORECASE)
        if match:
            source_alias = match.group(1).strip()
            edge_type = match.group(2).strip()
            props_str = '{' + match.group(3) + '}' if match.group(3) else ''
            target_alias = match.group(4).strip()
            
            props = self.parse_properties(props_str)
            return {
                "type": "CREATE_EDGE",
                "source_alias": source_alias,
                "target_alias": target_alias,
                "edge_type": edge_type,
                "properties": props
            }
        return None

    def parse_match(self, query):
        match_q = re.search(r'MATCH\s+(.*?)(?:\s+WHERE\s+(.*?))?(?:\s+RETURN\s+(.*))?$', query, re.IGNORECASE | re.DOTALL)
        if match_q:
            pattern_str = match_q.group(1).strip()
            where_str = match_q.group(2)
            return_str = match_q.group(3)

            node_matches = list(re.finditer(r'\((.*?)\)', pattern_str))
            edge_matches = list(re.finditer(r'-\[:(.*?)\]->', pattern_str))
            
            nodes = []
            for nm in node_matches:
                inner = nm.group(1).strip()
                if not inner:
                    nodes.append({})
                else:
                    alias, label = inner.split(':', 1) if ':' in inner else (inner, '')
                    nodes.append({"alias": alias.strip(), "label": label.strip()})

            edges = []
            for em in edge_matches:
                inner = em.group(1).strip()
                alias, etype = inner.split(':', 1) if ':' in inner else ('', inner)
                edges.append({"alias": alias.strip(), "type": etype.strip()})

            conditions = []
            if where_str:
                for cond in re.split(r'\s+AND\s+', where_str.strip(), flags=re.IGNORECASE):
                    cond_match = re.match(r'([a-zA-Z_]+)\.([a-zA-Z_]+)\s*(=|!=|>|<)\s*(.*)', cond.strip())
                    if cond_match:
                        alias = cond_match.group(1)
                        prop = cond_match.group(2)
                        op = cond_match.group(3)
                        val_str = cond_match.group(4).strip(' "\'')
                        val = int(val_str) if val_str.isdigit() else val_str
                        conditions.append((alias, prop, op, val))

            returns = []
            if return_str:
                for ret in return_str.split(','):
                    alias, prop = ret.strip().split('.')
                    returns.append((alias, prop))

            return {
                "type": "MATCH",
                "nodes": nodes,
                "edges": edges,
                "conditions": conditions,
                "returns": returns
            }
        return None

    def parse_shortest_path(self, query):
        match = re.match(r'SHORTEST_PATH\s+\((.*?)\)-\[\*(.*?)\.\.(.*?)\]->\((.*?)\)', query, re.IGNORECASE)
        if match:
            source_alias = match.group(1).strip()
            min_hops = int(match.group(2))
            max_hops = int(match.group(3))
            target_alias = match.group(4).strip()
            
            return {
                "type": "SHORTEST_PATH",
                "source_alias": source_alias,
                "target_alias": target_alias,
                "min_hops": min_hops,
                "max_hops": max_hops
            }
        return None

    def parse_stats(self, query):
        if query.strip().upper() == "STATS":
            return {"type": "STATS"}
        return None

    def parse(self, query):
        query = query.strip()
        if query.upper().startswith("CREATE NODE"):
            return self.parse_create_node(query)
        elif query.upper().startswith("CREATE EDGE"):
            return self.parse_create_edge(query)
        elif query.upper().startswith("MATCH"):
            return self.parse_match(query.replace('\n', ' '))
        elif query.upper().startswith("SHORTEST_PATH"):
            return self.parse_shortest_path(query)
        elif query.upper().startswith("STATS"):
            return self.parse_stats(query)
        else:
            return None
