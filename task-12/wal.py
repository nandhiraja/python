import json
import os
import time
from typing import List, Dict

class WALManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None

    def open(self):
        self.file = open(self.file_path, 'a')

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def append_mutation(self, mutation_type: str, data: dict):
        if not self.file:
            self.open()
        entry = {
            "timestamp": time.time(),
            "mutation": mutation_type,
            "data": data
        }
        self.file.write(json.dumps(entry) + "\n")
        self.file.flush()
        # Ensure it hits the disk
        os.fsync(self.file.fileno())

    def get_size(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return sum(1 for _ in f)
        return 0

    def recover(self) -> List[dict]:
        """Reads the WAL and returns a list of mutations to replay."""
        mutations = []
        if not os.path.exists(self.file_path):
            return mutations
        
        with open(self.file_path, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        mutations.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        pass # Ignore corrupted lines
        return mutations
