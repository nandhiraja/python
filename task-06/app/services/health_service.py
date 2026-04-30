from app.services.proxy_service import proxy_service


class HealthService:

    def get_dashboard(self, format_text: bool = False):
        result = []
        for service_name, metrics in proxy_service.metrics.items():
            breaker = proxy_service.circuit_breakers[service_name]
            result.append({
                "service": service_name,
                "status": metrics["status"],
                "latency": metrics["latency"],
                "circuit": breaker.state,
                "cache_hits": metrics["cache_hits"]
            })

        if not format_text:
            return result
            
        lines = []
        lines.append("=== Health Dashboard ===")
        lines.append("| Service          | Status | Latency | Circuit  | Cache Hits  |")
        for item in result:
            service = str(item["service"]).ljust(16)
            status = str(item["status"]).ljust(6)
            latency = str(item["latency"]).ljust(7)
            circuit = str(item["circuit"]).ljust(8)
            hits = f"{item['cache_hits']:,}".ljust(11)
            lines.append(f"| {service} | {status} | {latency} | {circuit} | {hits} |")
        return "\n".join(lines)

health_service = HealthService()