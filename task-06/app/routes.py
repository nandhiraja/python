import json
from fastapi import APIRouter, Request, Response
from app.services.proxy_service import proxy_service
from app.services.health_service import health_service
from app.config import SERVICES

router = APIRouter()

@router.get("/health")
async def health_dashboard():
    dashboard_text = health_service.get_dashboard(format_text=True)
    print(f"\n{dashboard_text}\n", flush=True)
    return Response(content=dashboard_text, media_type="text/plain")

@router.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        return Response(status_code=404, content=json.dumps({"error": "Service not found"}), media_type="application/json")
    
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    query_params = dict(request.query_params)
    
    response_data = await proxy_service.forward_request(
        service_name=service_name,
        path=path,
        method=request.method,
        headers=headers,
        body=body,
        query_params=query_params
    )
    
    if isinstance(response_data, dict) and "body" in response_data:
        resp_body = response_data["body"]
        if isinstance(resp_body, dict):
            content = json.dumps(resp_body).encode()
            media_type = "application/json"
        else:
            content = resp_body
            if isinstance(content, str):
                content = content.encode()
            media_type = response_data.get("headers", {}).get("content-type", "application/json")
            
        return Response(
            content=content,
            status_code=response_data.get("status", 500),
            media_type=media_type
        )
    return Response(status_code=500, content=json.dumps({"error": "Internal Server Error"}), media_type="application/json")
