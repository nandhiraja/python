## 15. Event-Driven Microservice with CQRS Pattern

**Description:** Implement a microservice separating read and write models (CQRS) with event sourcing. Commands emit domain events; handlers update read-optimized projections. Full event history is replayable.

**Prerequisites:**

- Domain-Driven Design (aggregates, commands, events)
- Event sourcing and append-only event stores
- Message bus / pub-sub (`Redis Streams`, `RabbitMQ`, or in-process)
- Eventual consistency concepts
- `asyncio` for async event handlers
- Two-database pattern (write store vs. read store)

