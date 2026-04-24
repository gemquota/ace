import os
import sys
import time
import asyncio
import sqlite3
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import uvicorn
import uvicorn.server

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from clide.storage import db

app = FastAPI(title="CAP Open-World MCP Server", version="1.0")

# 5-minute inactivity kill-switch
INACTIVITY_TIMEOUT = 300
last_activity = time.time()

def update_activity():
    global last_activity
    last_activity = time.time()

async def inactivity_monitor():
    """Kill-switch that shuts down the server after 5 minutes of inactivity."""
    while True:
        await asyncio.sleep(10)
        if time.time() - last_activity > INACTIVITY_TIMEOUT:
            print("[!] MCP SERVER: 5-minute inactivity kill-switch triggered. Shutting down.")
            # Sending signal to stop the uvicorn server gracefully
            import signal
            os.kill(os.getpid(), signal.SIGINT)
            break

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(inactivity_monitor())

@app.middleware("http")
async def activity_middleware(request: Request, call_next):
    update_activity()
    response = await call_next(request)
    return response

# --- REST Webhook & Read-Only Endpoints ---

@app.get("/events")
async def get_events(limit: int = 100):
    """Read-only endpoint for cap_events.db querying."""
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY logical_clock DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    events = db.get_events_by_trace(trace_id)
    if not events:
        raise HTTPException(status_code=404, detail="Trace not found")
    return events

# --- JSON-RPC Endpoint (MCP compatible) ---

@app.post("/rpc")
async def json_rpc_handler(request: Request):
    """JSON-RPC handler for dynamic MCP server logic."""
    try:
        payload = await request.json()
        method = payload.get("method")
        params = payload.get("params", {})
        request_id = payload.get("id", None)

        if not method:
            raise ValueError("Missing 'method' in JSON-RPC payload")

        result = await dispatch_rpc(method, params)

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": request_id if 'request_id' in locals() else None
        }

async def dispatch_rpc(method: str, params: Dict[str, Any]) -> Any:
    if method == "execute_intent":
        goal = params.get("goal")
        if not goal:
            raise ValueError("Missing 'goal' parameter")
        
        # We would normally route this to CapOrchestrator here.
        # But for this MCP server, we just return a simulated dispatch
        return {"status": "dispatched", "goal": goal, "message": "Intent execution started"}
    
    elif method == "get_status":
        return {"status": "active", "uptime": time.time() - last_activity}
    else:
        raise ValueError(f"Unknown method: {method}")

def spawn_mcp_server(host="127.0.0.1", port=8000):
    """On-Demand Spawner logic."""
    print(f"[*] SPAWNING MCP SERVER on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    spawn_mcp_server()
