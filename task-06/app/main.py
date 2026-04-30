from fastapi import FastAPI
from app.routes import router
from app.middleware.rate_limiter import rate_limit_middleware
from app.middleware.cache import cache_middleware
from starlette.middleware.base import BaseHTTPMiddleware

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Gateway Startup ", flush=True)
    print("[INFO] API Gateway running on http://0.0.0.0:8080", flush=True)
    print("[INFO] Routes loaded:", flush=True)
    from app.config import SERVICES
    for key, svc in SERVICES.items():
        padded_key = f"/api/{key}/**".ljust(16)
        print(f"       {padded_key} -> {svc.base_url}", flush=True)
    print("\n Request Log ", flush=True)
    yield

app = FastAPI(title="Async API Gateway", lifespan=lifespan)

app.add_middleware(BaseHTTPMiddleware, dispatch=cache_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

app.include_router(router)
