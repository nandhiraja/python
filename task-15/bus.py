import asyncio
from typing import List
from domain import Event

class MessageBus:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, event_type: type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def publish(self, topic: str, events: List[Event]):
        print(f"[BUS] Published {len(events)} events to \"{topic}\" topic\n")
        print("=== Event Handlers (Async) ===")
        
        tasks = []
        for event in events:
            handlers = self.handlers.get(type(event), [])
            for handler in handlers:
                tasks.append(asyncio.create_task(handler(event)))
                
        if tasks:
            await asyncio.gather(*tasks)
