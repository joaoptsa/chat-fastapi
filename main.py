import asyncio
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect,Request,Form, Depends, HTTPException
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketState
from pydantic import BaseModel
from fastapi import Query
from fastapi.responses import RedirectResponse


app = FastAPI()
templates = Jinja2Templates(directory="templates")


class SocketManager:
    
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []
        self.lock = asyncio.Lock()

    
    
    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append((websocket, user))

    
    
    async def disconnect(self, websocket: WebSocket, user: str):
        async with self.lock:
            if websocket.application_state == WebSocketState.CONNECTED:
                self.active_connections.remove((websocket, user))

    
    
    async def broadcast(self, data):
        async with self.lock:
            to_remove = []
            for connection in self.active_connections:
                websocket, _ = connection
                if websocket.application_state == WebSocketState.CONNECTED:
                    try:
                        await websocket.send_json(data)
                    except WebSocketDisconnect:
                    
                        to_remove.append(connection)

            for connection in to_remove:
                await self.disconnect(*connection)


    
    
    async def equal_name(self, name:str):
        async with self.lock:
            for _,user in self.active_connections:
                if name == user:
                    return True
            return False    


  
    
    async def send_personal_message(self, data, sender_websocket: WebSocket):
        async with self.lock:
            
            recipient_username = data.get("recipient", None)
            
            if recipient_username:recipient_connection = next(
                (connection for connection in self.active_connections if connection[1] == recipient_username),
                None)

            if recipient_connection:
                recipient_websocket, _ = recipient_connection
                await recipient_websocket.send_json(data)
                await sender_websocket.send_json(data)

            else:
               
                error_message = {"sender": "Server", "message": f"Recipient {recipient_username} not found"}
                await sender_websocket.send_json(error_message)
 

class RegisterValidator(BaseModel):
    username: str

manager = SocketManager()



@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


async def is_username_valid(user: str) -> bool:
    if len(user) > 3 and len(user) < 255:
        if await manager.equal_name(user)==False: 
            return True 
    return False



@app.post("/api/register")
async def register_user(form: RegisterValidator, response: Response):
    if await is_username_valid(form.username):
        print(form.username)
        response.status_code=200
        return {"content":"true"}  
    else:
        response.status_code = 400 
        return {"content": "false"}



@app.get("/chat")
def get_chat(request: Request, username: str = Query(..., alias="username")):
    if username == None:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("chat.html", {"request": request, "username": username})





@app.websocket("/api/chat")
async def chat(websocket: WebSocket, username: str):
    try:
        await manager.connect(websocket, username)
        response = {"sender": username, "message": "got connected"}
        await manager.broadcast(response)

        while websocket.application_state == WebSocketState.CONNECTED:
            
            try:
                data = await websocket.receive_json()

                if "recipient" in data:
                    
                    await manager.send_personal_message(data, websocket)
                else:
                    
                    await manager.broadcast(data)
            
            except WebSocketDisconnect:
                 
                 response = {"sender": username, "message": "left"}
                 await manager.broadcast(response)
                 break

    except WebSocketDisconnect:
        
        response = {"sender": username, "message": "left"}
        await manager.broadcast(response)

    except Exception as e:
        
        #response = {"sender": username, "message": "An error occurred"}
        await manager.disconnect(websocket, username)
        #await manager.broadcast(response)
    finally:
       
        await manager.disconnect(websocket, username)





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)




