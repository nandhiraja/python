import time
from fastapi import Request
from fastapi.responses import JSONResponse


class TokenBucket:

    def __init__(self, capacity: int, refill_rate: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow_request(self):
        now = time.time()
        elapsed = now - self.last_refill

        refill = elapsed * self.refill_rate

        self.tokens = min(
            self.capacity,
            self.tokens + refill
        )

        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False


class RateLimiter:

    def __init__(self):
        self.clients = {}

    def get_bucket(self, api_key: str):

        if api_key not in self.clients:
            self.clients[api_key] = TokenBucket(
                capacity=50,
                refill_rate=50 / 60
            )

        return self.clients[api_key]


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):

    api_key = request.headers.get("x-api-key", "anonymous")

    bucket = rate_limiter.get_bucket(api_key)

    if not bucket.allow_request():
        print(f"[REQ] {request.method} {request.url.path}  client={api_key}", flush=True)
        print(f"      -> RATE LIMITED ({int(bucket.tokens)}/{bucket.capacity} req/min) — 429 Too Many Requests\n", flush=True)
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests"
            }
        )

    return await call_next(request)