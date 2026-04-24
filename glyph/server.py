import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from src.backend.models import parse_gfs
from src.backend.engine import Engine

app = FastAPI(title="GFS-II Neural IDE")

LIB_FILE = 'library/programs.json'
os.makedirs('library', exist_ok=True)
DEFAULT_PROGRAM = "⟐(⊢◊(≈⟡⊣⌁)(≠✳⌬⇄)⊕)⟳"

if not os.path.exists(LIB_FILE):
    with open(LIB_FILE, 'w') as f: 
        json.dump({"Target Loop": DEFAULT_PROGRAM}, f)

engine_instance = Engine(parse_gfs(DEFAULT_PROGRAM))
running = False
connected_clients = []

class LoadRequest(BaseModel):
    text: str
    seed: int = 42

@app.get("/")
async def read_index(): 
    return FileResponse("web/index.html")

@app.get("/api/library")
async def get_library():
    with open(LIB_FILE, 'r') as f:
        return json.load(f)

@app.post("/api/play")
async def play_engine():
    global running
    running = True
    return {"status": "running"}

@app.post("/api/pause")
async def pause_engine():
    global running
    running = False
    return {"status": "paused"}

@app.post("/api/load")
async def load_engine(req: LoadRequest):
    global running, engine_instance
    running = False
    engine_instance = Engine(parse_gfs(req.text), seed=req.seed)
    
    state = engine_instance.get_state()
    for client in connected_clients:
        await client.send_json(state)
        
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await websocket.send_json(engine_instance.get_state())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def engine_daemon():
    global running, engine_instance
    loop = asyncio.get_event_loop()
    while True:
        if running and engine_instance:
            try:
                await loop.run_in_executor(None, engine_instance.step)
                state = engine_instance.get_state()
                for client in connected_clients:
                    await client.send_json(state)
            except Exception as e:
                print(f"Engine Step Error: {e}")
                running = False
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(engine_daemon())

if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8082)
