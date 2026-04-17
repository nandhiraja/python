from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.rooms:dict= {'general':[],
                          'office':[],
                          'coder':[],
                          'designer':[],
                          'helper':[]
                          }
        
        self.user_map: dict ={}
        self.active_connections: dict = {} 
        self.rooms_history : dict ={'general':[],
                                     'office':[],
                                     'coder':[],
                                     'designer':[],
                                     'helper':[]
                                     }

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections[user_id]
    
    async def join_room(self,user_id,room,websocket: WebSocket):
        if room not in self.rooms:
            self.rooms[room]=[]
        if websocket in self.rooms[room]:
            print('Already user present..')
            return

        self.rooms[room].append(websocket)
        self.user_map[user_id].append(room)
        await self.send_activate_room(user_id,websocket)

    async def send_activate_room(self,user_id,websocket):
        if user_id not in self.user_map:
            self.user_map[user_id]=[]
        message ={
            'type':"activate-room",
            "user":user_id,
            'activatedRoom':self.user_map[user_id]
        }
        print(message)
        await websocket.send_json(message)
        

    async def broadcast(self, room: str, message: dict):
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_json(message)
    async def send_initial_data(self,user_id:str,websocket:WebSocket):
        rooms =[]
        
        for room in self.rooms.keys():
            rooms.append(room.capitalize())
        message={
            'type':'available-rooms',
            'user':user_id,
            'online':len(self.active_connections),
            'availableRooms':rooms
        }
        await websocket.send_json(message)

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            print("sending to client: ", user_id)
            await self.active_connections[user_id].send_json(message)
    
    async def send_history(self,room,websocket:WebSocket):
        message = {
            'type':'chat-history',
            'room':room,
            'online':len(self.active_connections),

            'history': self.rooms_history[room]
        }
        await websocket.send_json(message)
    async def send_typing_info(self,user_id,room):
        print('sending.. typing to frontend')
        message={
            'type':'typing',
             'user':user_id,
             'room':room
        }
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_json(message)
                

    async def update_history(self,room,message):
        self.rooms_history[room].append(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    await manager.send_activate_room(user_id,websocket)
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if(data['type']=='room-join'):
                await manager.join_room(data['user'],data['room'].lower(),websocket)

            elif(data['type']=='chat-message'):
                print(data) 
                message = { 'type':'chat-message',
                            'user':data['user'],
                           'text': data['message'],
                           'room': data['room'] ,
                           'timestamp': data['timestamp'],
                            'online':len(manager.active_connections)
                           } 
                print(message) 
                await manager.broadcast(data['room'].lower(),message )
                await manager.update_history(data['room'].lower(),message )


            elif(data['type']=='initial-data'):
               await manager.send_initial_data(data['user'],websocket)

            elif(data['type']=='chat-history'):
                await manager.send_history(data['room'].lower(),websocket)              
            elif(data['type']=='typing'):
                print("receive typing......",data)

                await manager.send_typing_info(data['user'],data['room'])
            else:
                print("Sorry no process......")


    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app',host='localhost',port=8080,reload=True)