## Async API Gateway with Rate Limiting & Caching

**Description:** Build a reverse-proxy API gateway that routes requests to downstream microservices. Implement token-bucket rate limiting, response caching with TTL, and circuit-breaker patterns.

**Prerequisites:**

- `asyncio` event loop and coroutines
- `aiohttp` or `FastAPI` framework
- Token-bucket rate limiting algorithm
- Redis for caching (`aioredis`)
- Circuit breaker design pattern
- HTTP reverse proxy concepts
- Middleware pattern