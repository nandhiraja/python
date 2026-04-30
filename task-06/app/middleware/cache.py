import json
import time

from fastapi import Request
from fastapi.responses import Response

from app.services.redis_service import redis_service


CACHEABLE_METHODS = {"GET"}


async def cache_middleware(request: Request, call_next):
    start_time = time.time()

    if request.method not in CACHEABLE_METHODS:
        return await call_next(request)

    cache_key = f"cache:{request.url.path}"

    cached = await redis_service.get(cache_key)

    if cached:

        ttl = await redis_service.ttl(cache_key)

        api_key = request.headers.get("x-api-key", "anonymous")
        latency_ms = int((time.time() - start_time) * 1000)
        print(f"[REQ] {request.method} {request.url.path}  client={api_key}", flush=True)
        print(f"      -> CACHE HIT (TTL: {ttl}s remaining) — 200 OK in {latency_ms}ms\n", flush=True)
        
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 2 and path_parts[0] == "api":
            from app.config import SERVICES
            from app.services.proxy_service import proxy_service
            svc_id = path_parts[1]
            if svc_id in SERVICES:
                proxy_service.metrics[SERVICES[svc_id].name]["cache_hits"] += 1

        return Response(
            content=cached,
            media_type="application/json"
        )

    response = await call_next(request)

    body = b""

    async for chunk in response.body_iterator:
        body += chunk

    await redis_service.set(
        cache_key,
        body.decode(),
        ttl=60
    )

    return Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )