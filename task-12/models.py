import json

class Node:
    def __init__(self, node_id, label, properties=None):
        self.node_id = node_id
        self.label = label
        self.properties = properties or {}

    def to_dict(self):
        return {
            "type": "NODE",
            "id": self.node_id,
            "label": self.label,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["label"], data["properties"])

    def __str__(self):
        return f"{self.label}#{self.node_id}"

class Edge:
    def __init__(self, edge_id, source_id, target_id, edge_type, properties=None):
        self.edge_id = edge_id
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type
        self.properties = properties or {}

    def to_dict(self):
        return {
            "type": "EDGE",
            "id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.type,
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["source_id"], data["target_id"], data["edge_type"], data["properties"])

    def __str__(self):
        return f"Node#{self.source_id} —{self.type}-> Node#{self.target_id}"
