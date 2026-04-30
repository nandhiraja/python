import httpx
import time

from app.config import SERVICES
from app.services.circuit_breaker import CircuitBreaker


class ProxyService:

    def __init__(self):

        self.client = httpx.AsyncClient(timeout=10)

        self.circuit_breakers = {
            service.name: CircuitBreaker()
            for service in SERVICES.values()
        }

        self.metrics = {
            service.name: {
                "cache_hits": 0,
                "latency": 0,
                "status": "UP"
            }
            for service in SERVICES.values()
        }

    async def forward_request(
        self,
        service_name: str,
        path: str,
        method: str,
        headers: dict,
        body: bytes = None,
        query_params=None
    ):

        service = SERVICES[service_name]

        api_key = headers.get("x-api-key", "anonymous")
        full_path = f"/api/{service_name}/{path}"
        
        circuit = self.circuit_breakers[service.name]

        if not circuit.can_execute():
            print(f"[REQ] {method} {full_path}  client={api_key}", flush=True)
            print(f"      -> CIRCUIT OPEN ({service.name}) — 503 Service Unavailable\n", flush=True)
            return {
                "status": 503,
                "body": {
                    "error": "Service temporarily unavailable",
                    "retry_after": 30
                }
            }

        target_url = f"{service.base_url}/{path}"

        start_time = time.time()
        try:

            response = await self.client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=query_params,
                content=body
            )

            circuit.record_success()
            
            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics[service.name]["latency"] = f"{latency_ms}ms"
            self.metrics[service.name]["status"] = "UP"

            print(f"[REQ] {method} {full_path}  client={api_key}", flush=True)
            print(f"      -> PROXY to {service.name} — {response.status_code} OK in {latency_ms}ms\n", flush=True)

            return {
                "status": response.status_code,
                "body": response.text,
                "headers": response.headers
            }

        except Exception as e:

            circuit.record_failure()

            self.metrics[service.name]["status"] = "DOWN"
            self.metrics[service.name]["latency"] = "timeout"

            return {
                "status": 503,
                "body": {
                    "error": str(e)
                }
            }


proxy_service = ProxyService()