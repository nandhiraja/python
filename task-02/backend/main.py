from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.rooms:dict= {'general':[],
                          'office':[],
                          'coder':[]
                          }
        
        self.user_map: dict ={}
        self.active_connections: dict = {} 

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]
    
    async def join_room(self,room,websocket: WebSocket):
        if room not in self.rooms:
            self.rooms[room]=[]
        self.rooms[room].append(websocket)
        print(self.rooms)

    async def broadcast(self, room: str, message: dict):
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_json(message)


    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            print("sending to client: ", user_id)
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if(data['type']=='room-join'):
                await manager.join_room(data['room'],websocket)

            elif(data['type']=='chat-message'):
                print(data) 
                message = {'user':data['user'],
                           'text': data['message'],
                           'room': data['room'] ,
                           'timestamp': data['timestamp']
                           } 
                print(message) 
                await manager.broadcast(data['room'],message )
            else:
                print("Sorry no process......")


    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app',host='localhost',port=8080,reload=True)