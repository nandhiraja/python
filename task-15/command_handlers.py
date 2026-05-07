from domain import PlaceOrderCommand, OrderPlaced, InventoryReserved
from event_store import EventStore
from bus import MessageBus

class OrderCommandHandler:
    def __init__(self, event_store: EventStore, bus: MessageBus):
        self.event_store = event_store
        self.bus = bus
        self.next_order_id = 1087

    async def handle_place_order(self, cmd: PlaceOrderCommand):
        print("[WRITE] PlaceOrderCommand received")
        order_id = f"ORD-{self.next_order_id}"
        self.next_order_id += 1
        print(f"[WRITE] Aggregate Order#{order_id} created")
        
        total = sum(item['qty'] * item['price'] for item in cmd.items)
        
        events = []
        order_placed = OrderPlaced(aggregate_id=order_id, timestamp="2026-02-24T14:32:01Z", customer_id=cmd.customer_id, total=total, items=cmd.items)
        events.append(order_placed)
        
        for item in cmd.items:
            events.append(InventoryReserved(aggregate_id=order_id, sku=item['sku'], qty=item['qty'], timestamp="2026-02-24T14:32:01Z"))
            
        self.event_store.append_events(order_id, events)
        await self.bus.publish("orders", events)
