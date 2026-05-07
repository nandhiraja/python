from typing import List, Dict
from domain import Event, OrderPlaced, InventoryReserved, Order

class EventStore:
    def __init__(self):
        self._store: Dict[str, List[Event]] = {}

    def append_events(self, aggregate_id: str, events: List[Event]):
        if aggregate_id not in self._store:
            self._store[aggregate_id] = []
        self._store[aggregate_id].extend(events)
        
        print("[EVENT STORE] Appended events:")
        for i, ev in enumerate(events, 1):
            if isinstance(ev, OrderPlaced):
                print(f"  {i}. OrderPlaced       {{order_id: \"{aggregate_id}\", customer: \"{ev.customer_id}\", total: ${ev.total:.2f}}}")
            elif isinstance(ev, InventoryReserved):
                print(f"  {i}. InventoryReserved {{sku: \"{ev.sku}\", qty: {ev.qty}}}")

    def get_events(self, aggregate_id: str) -> List[Event]:
        return self._store.get(aggregate_id, [])

    def replay(self, aggregate_id: str) -> Order:
        events = self.get_events(aggregate_id)
        aggregate = Order(aggregate_id)
        for event in events:
            aggregate.apply(event)
        return aggregate
