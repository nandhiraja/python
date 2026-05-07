import asyncio
from domain import OrderPlaced
from read_store import ReadStore

class OrderDashboardProjection:
    def __init__(self, read_store: ReadStore):
        self.read_store = read_store

    async def handle_order_placed(self, event: OrderPlaced):
        print("[HANDLER: OrderDashboardProjection] OrderPlaced -> updating read model...")
        item_count = sum(i['qty'] for i in event.items)
        
        self.read_store.order_summary[event.aggregate_id] = {
            "order_id": event.aggregate_id,
            "customer_id": event.customer_id,
            "status": "PLACED",
            "total": round(event.total, 2),
            "item_count": item_count,
            "placed_at": event.timestamp
        }
        print(f"  Read DB: INSERT INTO order_summary (id, customer, total, status, item_count)")
        print(f"           VALUES ('{event.aggregate_id}', '{event.customer_id}', {event.total:.2f}, 'PLACED', {item_count})\n")


class NotificationService:
    async def handle_order_placed(self, event: OrderPlaced):
        print("[HANDLER: NotificationService] OrderPlaced -> sending confirmation email...")
        await asyncio.sleep(0.01) 
        print(f"  Email sent to customer {event.customer_id} OK\n")


class AnalyticsProjection:
    def __init__(self):
        self.daily_revenue = 12607.36

    async def handle_order_placed(self, event: OrderPlaced):
        print("[HANDLER: AnalyticsProjection] OrderPlaced -> updating daily stats...")
        self.daily_revenue += event.total
        print(f"  Today's revenue: ${self.daily_revenue:,.2f} (+${event.total:.2f})\n")
