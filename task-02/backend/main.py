from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {} 

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())            
            await manager.send_personal_message(f"message: {data['message']}", data['user'] )


    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app',host='localhost',port=8080,reload=True)