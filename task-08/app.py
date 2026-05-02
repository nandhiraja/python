import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sensor import sensor_stream
from processor import StreamProcessor

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[INFO] {len(self.active_connections)} clients connected", flush=True)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[INFO] {len(self.active_connections)} clients connected", flush=True)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()
processor = StreamProcessor(window_size=300)

@app.on_event("startup")
async def startup_event():
    print("=== Server Console ===", flush=True)
    print("[INFO] Stream processor started — consuming from sensors/factory-a", flush=True)
    print("[INFO] Dashboard available at http://localhost:5000/dashboard", flush=True)
    print("\n=== Live Sensor Feed (every 1s) ===", flush=True)
    asyncio.create_task(process_stream())

async def process_stream():
    async for raw_data in sensor_stream("sensor-T1"):
        processed_data = processor.process_point(raw_data)
        
        time_str = datetime.fromisoformat(processed_data["timestamp"]).strftime("%H:%M:%S")
        
        temp = processed_data["temperature"]
        vib = processed_data["vibration"]
        status = processed_data["status"]
        
        print(f"[{time_str}] {processed_data['sensor_id']}  temp={temp}F  vibration={vib}g  status={status}", flush=True)
        
        alert = processed_data["alert"]
        if alert:
            sign = "+" if alert["sigma"] > 0 else ""
            print(" Alert Triggered ", flush=True)
            print(f"[ALERT] {alert['sensor_id']} — {alert['message']}", flush=True)
            print(f"        Current: {alert['current']}F | 5-min avg: {alert['avg_5m']}F | Deviation: {sign}{alert['sigma']} sigma", flush=True)
            print(f"        Action: Notification sent to ops-team@factory.com\n", flush=True)
            
            print(" Live Sensor Feed (every 1s) ", flush=True)

        await manager.broadcast(processed_data)

@app.get("/dashboard")
async def get_dashboard():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
