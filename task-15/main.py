import asyncio
import json
from domain import PlaceOrderCommand, OrderPlaced, OrderUpdated, PaymentProcessed, OrderShipped, InventoryReserved
from event_store import EventStore
from read_store import ReadStore, GetOrderSummary
from bus import MessageBus
from command_handlers import OrderCommandHandler
from event_handlers import OrderDashboardProjection, NotificationService, AnalyticsProjection

async def main():
    print("=== Command Side (Write) ===")
    
    event_store = EventStore()
    read_store = ReadStore()
    bus = MessageBus()
    
    dashboard_proj = OrderDashboardProjection(read_store)
    notification_svc = NotificationService()
    analytics_proj = AnalyticsProjection()
    
    bus.subscribe(OrderPlaced, dashboard_proj.handle_order_placed)
    bus.subscribe(OrderPlaced, notification_svc.handle_order_placed)
    bus.subscribe(OrderPlaced, analytics_proj.handle_order_placed)
    
    order_handler = OrderCommandHandler(event_store, bus)
    
    print('>>> cmd = PlaceOrderCommand(customer_id="C-42", items=[')
    print('...     {"sku": "WIDGET-01", "qty": 3, "price": 29.99},')
    print('...     {"sku": "GADGET-05", "qty": 1, "price": 149.99}')
    print('... ])')
    print('>>> bus.dispatch(cmd)\n')
    
    cmd = PlaceOrderCommand(customer_id="C-42", items=[
        {"sku": "WIDGET-01", "qty": 3, "price": 29.99},
        {"sku": "GADGET-05", "qty": 1, "price": 149.99}
    ])
    
    await order_handler.handle_place_order(cmd)
    
    print("=== Query Side (Read) ===")
    print('>>> query = GetOrderSummary(order_id="ORD-1087")')
    print('>>> result = read_store.execute(query)')
    
    query = GetOrderSummary(order_id="ORD-1087")
    result, elapsed_ms = read_store.execute(query)
    
    print(json.dumps(result, indent=2))
    print(f"Response time: {elapsed_ms:.1f}ms (denormalized read model)\n")
    
    print("=== Event Replay (Audit) ===")
    print('>>> events = event_store.get_events(aggregate_id="ORD-1087")')
    
    time_events = [
        OrderUpdated(aggregate_id="ORD-1087", timestamp="2026-02-24T14:45:22Z", removed="GADGET-05", new_total=89.97),
        PaymentProcessed(aggregate_id="ORD-1087", timestamp="2026-02-24T14:46:01Z", amount=89.97, method="card_ending_4242"),
        OrderShipped(aggregate_id="ORD-1087", timestamp="2026-02-24T15:10:33Z", tracking="1Z999AA10123456784")
    ]
    
    event_store._store["ORD-1087"].extend(time_events)
    
    events = event_store.get_events("ORD-1087")
    disp_i = 1
    for ev in events:
        if isinstance(ev, InventoryReserved):
            continue
            
        ts = ev.timestamp.split('T')[1].replace('Z', '')
        if isinstance(ev, OrderPlaced):
            print(f"[Event #{disp_i}] OrderPlaced       @ {ts}  {{total: {ev.total:.2f}, status: PLACED}}")
        elif isinstance(ev, OrderUpdated):
            print(f"[Event #{disp_i}] OrderUpdated      @ {ts}  {{removed: \"{ev.removed}\", new_total: {ev.new_total:.2f}}}")
        elif isinstance(ev, PaymentProcessed):
            print(f"[Event #{disp_i}] PaymentProcessed  @ {ts}  {{amount: {ev.amount:.2f}, method: \"{ev.method}\"}}")
        elif isinstance(ev, OrderShipped):
            print(f"[Event #{disp_i}] OrderShipped      @ {ts}  {{tracking: \"{ev.tracking}\"}}")
        disp_i += 1
            
    print('\n>>> rebuild = event_store.replay("ORD-1087")')
    rebuild = event_store.replay("ORD-1087")
    print(f"Reconstructed state: {rebuild}")

if __name__ == "__main__":
    asyncio.run(main())
