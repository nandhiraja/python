from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Command:
    pass

@dataclass
class PlaceOrderCommand(Command):
    customer_id: str
    items: List[Dict[str, Any]]

@dataclass
class Event:
    aggregate_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

@dataclass
class OrderPlaced(Event):
    customer_id: str = ""
    total: float = 0.0
    items: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class InventoryReserved(Event):
    sku: str = ""
    qty: int = 0

@dataclass
class OrderUpdated(Event):
    removed: str = ""
    new_total: float = 0.0

@dataclass
class PaymentProcessed(Event):
    amount: float = 0.0
    method: str = ""

@dataclass
class OrderShipped(Event):
    tracking: str = ""

class Order:
    def __init__(self, aggregate_id: str):
        self.id = aggregate_id
        self.status = "CREATED"
        self.total = 0.0
        self.customer_id = None
        self.items = []

    def apply(self, event: Event):
        if isinstance(event, OrderPlaced):
            self.customer_id = event.customer_id
            self.total = event.total
            self.status = "PLACED"
            self.items = event.items
        elif isinstance(event, OrderUpdated):
            self.items = [i for i in self.items if i['sku'] != event.removed]
            self.total = event.new_total
        elif isinstance(event, PaymentProcessed):
            self.status = "PAID"
        elif isinstance(event, OrderShipped):
            self.status = "SHIPPED"
            
    def __repr__(self):
        return f"Order(id={self.id}, status={self.status}, total={self.total:.2f}, items={len(self.items)})"
