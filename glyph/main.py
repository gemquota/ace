import os
import json
import asyncio
import sqlite3
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from src.backend.models import parse_gfs
from src.backend.engine import Engine

app = FastAPI(title="GFS-III Neural IDE")

LIB_FILE = 'library/programs.json'
os.makedirs('library', exist_ok=True)
DEFAULT_PROGRAM = "⟐(⊢◊(≈⟡⊣⌁)(≠✳⌬⇄)⊕)⟳"

def seed_library():
    if not os.path.exists(LIB_FILE):
        with open(LIB_FILE, 'w') as f: 
            json.dump({"Target Loop": DEFAULT_PROGRAM}, f)
seed_library()

broadcast_queue = asyncio.Queue()
engine_instance = Engine(parse_gfs(DEFAULT_PROGRAM), broadcast_queue=broadcast_queue)
running = False

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

class LoadRequest(BaseModel):
    text: str
    seed: int = 42

@app.get("/")
async def read_index(): return FileResponse("web/index.html")

@app.get("/api/state")
async def get_state(): return engine_instance.get_state()

@app.get("/api/history")
async def get_history():
    db = sqlite3.connect("metrics.db", check_same_thread=False)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    # Fetch latest 1000 events to keep it fast
    c.execute("SELECT * FROM telemetry ORDER BY tick DESC LIMIT 1000")
    rows = c.fetchall()
    return [dict(r) for r in reversed(rows)]

@app.post("/api/step")
async def step_engine():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, engine_instance.step)
    
    # Broadcast full state after stepping manually
    state_msg = json.dumps({"type": "state", "data": engine_instance.get_state()})
    broadcast_queue.put_nowait(state_msg)
    
    return {"status": "ok"}

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
    engine_instance = Engine(parse_gfs(req.text), seed=req.seed, broadcast_queue=broadcast_queue)
    
    state_msg = json.dumps({"type": "state", "data": engine_instance.get_state()})
    broadcast_queue.put_nowait(state_msg)
    
    return {"status": "ok"}

@app.get("/api/library")
async def get_library():
    with open(LIB_FILE, 'r') as f: return json.load(f)

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps({"type": "state", "data": engine_instance.get_state()}))
        while True:
            data = await websocket.receive_text()
            # Handle remote orchestration commands
            try:
                cmd = json.loads(data)
                if cmd.get("action") == "pause":
                    global running
                    running = False
            except:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def telemetry_broadcaster():
    while True:
        try:
            message = await broadcast_queue.get()
            await manager.broadcast(message)
            broadcast_queue.task_done()
        except Exception as e:
            print(f"Broadcast Error: {e}")

async def engine_daemon():
    global running, engine_instance
    loop = asyncio.get_event_loop()
    while True:
        if running and engine_instance:
            try:
                await loop.run_in_executor(None, engine_instance.step)
                # Broadcast state every tick if running
                state_msg = json.dumps({"type": "state", "data": engine_instance.get_state()})
                broadcast_queue.put_nowait(state_msg)
            except Exception as e:
                print(f"Engine Step Error: {e}")
                running = False
        await asyncio.sleep(0.5) # Engine tick delay

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(engine_daemon())
    asyncio.create_task(telemetry_broadcaster())

if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
