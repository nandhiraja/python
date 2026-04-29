from dataclasses import dataclass


@dataclass
class ServiceConfig:
    name: str
    base_url: str


SERVICES = {
    "users": ServiceConfig(
        name="user-service",
        base_url="http://localhost:3001"
    ),
    "orders": ServiceConfig(
        name="order-service",
        base_url="http://localhost:3002"
    ),
    "products": ServiceConfig(
        name="product-service",
        base_url="http://localhost:3003"
    )
}

RATE_LIMIT_PER_MINUTE = 50
CACHE_TTL_SECONDS = 60
CIRCUIT_FAILURE_THRESHOLD = 5
CIRCUIT_RECOVERY_TIMEOUT = 30