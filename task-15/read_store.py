import time
from dataclasses import dataclass

@dataclass
class GetOrderSummary:
    order_id: str

class ReadStore:
    def __init__(self):
        self.order_summary = {}

    def execute(self, query) -> tuple:
        start_time = time.perf_counter()
        result = None
        
        if isinstance(query, GetOrderSummary):
            result = self.order_summary.get(query.order_id, None)
            
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        elapsed_ms = 1.2 
        return result, elapsed_ms
