import os
import sys
import time
import json
import sqlite3
import asyncio
import contextlib
import io
import random
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import pydantic

# Project paths
CORE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROJECT_ROOT = os.path.dirname(CORE_DIR)
sys.path.insert(0, CORE_DIR)

# Data paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

VERSION = "2.0.0" # Fallback
try:
    with open(os.path.join(PROJECT_ROOT, "VERSION"), "r") as f:
        VERSION = f.read().strip()
except: pass

from clide.storage import db
from clide.kernel import orchestrator
from clide.kernel import syscalls
from pie.engine import PieEngine
from pie.inference import PieInference
from clide.observability.aggregator import ObservabilityAggregator
from clide.observability.stream_processor import StreamProcessor
from clide.observability.state_builder import StateBuilder
from clide.observability.graph_builder import GraphBuilder
from clide.control.permissions import ControlRole, ActionType
from clide.control.controller import ControlRouter
from clide.control.policy import PolicyEngine
from clide.kernel.goal_manager import GoalManager

app = FastAPI(title="CAP Observability Dashboard", version=VERSION)

# --- Observability Stack ---
aggregator = ObservabilityAggregator()
stream_processor = StreamProcessor(aggregator)
graph_builder = GraphBuilder()

# --- Subsystem Telemetry ---
class SubsystemStreamManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "CLIDE": [],
            "APC": [],
            "PIE": [],
            "ACE": [],
            "GLYPH": []
        }

    async def connect(self, websocket: WebSocket, subsystem_id: str):
        await websocket.accept()
        if subsystem_id in self.active_connections:
            self.active_connections[subsystem_id].append(websocket)
            print(f"[*] SUBSYSTEM WS: {subsystem_id} connected.")
        else:
            print(f"[!] SUBSYSTEM WS: Unknown ID {subsystem_id}")

    def disconnect(self, websocket: WebSocket, subsystem_id: str):
        if subsystem_id in self.active_connections:
            self.active_connections[subsystem_id].remove(websocket)
            print(f"[*] SUBSYSTEM WS: {subsystem_id} disconnected.")

    async def broadcast_to_subsystem(self, subsystem_id: str, message: Dict[str, Any]):
        if subsystem_id not in self.active_connections:
            return
        
        # Cleanup closed sockets
        dead_connections = []
        for connection in self.active_connections[subsystem_id]:
            try:
                await connection.send_json(message)
            except:
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.active_connections[subsystem_id].remove(dead)

    async def route_event(self, message: Dict[str, Any]):
        """Routes generic cognitive events to specific subsystem streams with ACE_EVENT_BUS headers."""
        # 1. Normalize message to ACE_EVENT_BUS Header format
        if "trace_id" not in message:
            event_data = message.get("event", {})
            normalized_message = {
                "trace_id": event_data.get("trace_id", "GLOBAL"),
                "source": "CLIDE", # Default source for polled events
                "type": message.get("type", "COGNITIVE_EVENT"),
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                "payload": message
            }
        else:
            normalized_message = message

        # 2. Extract layer for subsystem routing
        payload = normalized_message.get("payload", {})
        event = payload.get("event", {}) if normalized_message["type"] == "COGNITIVE_EVENT" else payload
        layer = event.get("layer")
        
        # Mapping Layer to Subsystem
        if layer == "CLIDE":
            await self.broadcast_to_subsystem("CLIDE", normalized_message)
        elif layer == "APC":
            await self.broadcast_to_subsystem("APC", normalized_message)
        elif layer == "PXE":
            # PIE consumes PXE layer events (Inference)
            await self.broadcast_to_subsystem("PIE", normalized_message)
        elif layer == "ACE":
            await self.broadcast_to_subsystem("ACE", normalized_message)
        elif layer == "GLYPH":
            await self.broadcast_to_subsystem("GLYPH", normalized_message)

subsystem_manager = SubsystemStreamManager()
stream_processor.subscribe(subsystem_manager.route_event)

# --- Control Stack ---
policy_engine = PolicyEngine()
control_router = ControlRouter(user_role=ControlRole.ADMIN, policy_engine=policy_engine)
goal_manager = GoalManager()

# --- Models ---
class GoalRequest(pydantic.BaseModel):
    goal: str
    trace_id: Optional[str] = None
    use_queue: bool = False
    routing: str = "DIRECT"
    target_id: Optional[str] = None

class DiagnoseRequest(pydantic.BaseModel):
    trace_id: str

# --- State ---
active_traces = {} # trace_id -> status
trace_logs = {}   # trace_id -> io.StringIO

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    with open(os.path.join(static_dir, "index.html"), "r") as f:
        return f.read()

from pie.reasoning import PieReasoningEngine
reasoning_engine = PieReasoningEngine(DATA_DIR)

# --- Autonomous Swarm Background Task ---
async def autonomous_swarm_loop():
    """Simulates agents using a real reasoning engine to make decisions."""
    print("[*] Starting PIE Autonomous Swarm Loop...")
    while True:
        try:
            swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
            if os.path.exists(swarm_db):
                with sqlite3.connect(swarm_db) as conn:
                    conn.row_factory = sqlite3.Row
                    agents = conn.execute("SELECT * FROM agent_wallets").fetchall()
                    if not agents:
                        conn.execute("INSERT INTO agent_wallets (agent_id, balance, last_updated) VALUES (?, 1000.0, ?)", ("prime", int(time.time())))
                        conn.commit()
                        agents = conn.execute("SELECT * FROM agent_wallets").fetchall()
                    
                    agent = random.choice(agents)
                    
                    # 2. Use Reasoning Engine to Decide Action
                    decision = reasoning_engine.decide_action(agent["agent_id"], agent["balance"])
                    action = decision["action"]
                    reason = decision["reason"]
                    
                    if action == "BUY":
                        intents = conn.execute("SELECT * FROM intents WHERE owner_agent_id != ?", (agent["agent_id"],)).fetchall()
                        if intents:
                            intent = random.choice(intents)
                            if agent["balance"] >= intent["price"]:
                                print(f"[*] AUTO: Agent {agent['agent_id'][:8]} buying {intent['name']} - REASON: {reason}")
                                conn.execute("UPDATE agent_wallets SET balance = balance - ? WHERE agent_id = ?", (intent["price"], agent["agent_id"]))
                                conn.execute("UPDATE agent_wallets SET balance = balance + ? WHERE agent_id = ?", (intent["price"], intent["owner_agent_id"]))
                                conn.execute("UPDATE intents SET owner_agent_id = ? WHERE id = ?", (agent["agent_id"], intent["id"]))
                                conn.execute("INSERT INTO credit_ledger (agent_id, amount, transaction_type, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                                             (agent["agent_id"], -intent["price"], "SPENT", f"AUTO: {reason}", int(time.time())))
                                conn.commit()
                    elif action == "LIST":
                        intent_names = ["PROMPT_OPTIMIZER", "CODE_SQUASH", "TRACE_PRUNER", "CAUSAL_MAPPER", "KERNEL_PATCH", "SWARM_DASH"]
                        name = random.choice(intent_names) + "_" + str(random.randint(100, 999))
                        price = random.uniform(5.0, 50.0)
                        
                        existing = conn.execute("SELECT id FROM intents WHERE name = ?", (name,)).fetchone()
                        if not existing:
                            print(f"[*] AUTO: Agent {agent['agent_id'][:8]} listing new intent: {name} - REASON: {reason}")
                            conn.execute("INSERT INTO intents (name, description, actions, price, owner_agent_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                                         (name, f"Autonomous {name} service", "[]", price, agent["agent_id"], int(time.time())))
                            conn.commit()
        except Exception as e:
            print(f"[!] Swarm Loop Error: {e}")
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(autonomous_swarm_loop())
    asyncio.create_task(stream_processor.poll_and_process())

# --- REST APIs ---

@app.get("/api/status")
async def get_system_status():
    arch_model_path = os.path.join(DATA_DIR, "cap_arch_model.json")
    try:
        if os.path.exists(arch_model_path):
            with open(arch_model_path, "r") as f:
                data = json.load(f)
                data["version"] = VERSION
                return data
    except: pass
    return {"status": "error", "message": "Could not load architecture model", "version": VERSION}

@app.post("/api/init")
async def initialize_system():
    db.init_db()
    return {"status": "success", "message": "Database initialized"}

@app.post("/api/execute")
async def execute_goal(request: GoalRequest, background_tasks: BackgroundTasks):
    trace_id = request.trace_id or syscalls.cap_trace_start()
    
    actual_goal = request.goal
    target_id = request.target_id or "prime"
    
    if request.routing == "OVERSEER":
        actual_goal = f"[OVERSEER_VETTING] {request.goal}"
    elif request.routing == "COLLECTIVE":
        actual_goal = f"[COLLECTIVE_BROADCAST] {request.goal}"
    
    syscalls.cap_event_commit(trace_id=trace_id, layer=syscalls.Layer.CLIDE, event_type=syscalls.EventType.GOAL_GENERATED, 
                               payload={"goal": actual_goal, "type": "USER_INJECTION", "routing": request.routing, "target": target_id}, causal_parent=None)
    
    def run_goal(gid, goal_str, queue_mode, agent_id):
        active_traces[gid] = "RUNNING"
        log_buffer = io.StringIO()
        trace_logs[gid] = log_buffer
        try:
            with contextlib.redirect_stdout(log_buffer), contextlib.redirect_stderr(log_buffer):
                cap = orchestrator.CapOrchestrator(trace_id=gid, agent_id=agent_id)
                cap.execute_goal(goal_str, use_queue=queue_mode)
            active_traces[gid] = "COMPLETED"
        except Exception as e:
            active_traces[gid] = f"FAILED: {str(e)}"
        finally:
            log_dir = os.path.join(LOGS_DIR, "traces")
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, f"{gid}.log"), "w") as f: f.write(log_buffer.getvalue())
    background_tasks.add_task(run_goal, trace_id, actual_goal, request.use_queue, target_id)
    return {"status": "success", "trace_id": trace_id}

@app.get("/api/trace_status/{trace_id}")
async def get_trace_status(trace_id: str):
    status = active_traces.get(trace_id, "UNKNOWN")
    logs = trace_logs[trace_id].getvalue() if trace_id in trace_logs else ""
    return {"status": status, "logs": logs}

@app.post("/api/diagnose")
async def diagnose_trace(request: DiagnoseRequest):
    try:
        pie_engine = PieEngine()
        events = pie_engine.load_trace(request.trace_id)
        if not events: return {"status": "error", "message": "No events found"}
        inf = PieInference(events)
        state = inf.analyze(active_flavours=["diagnostic"])
        return {"status": "success", "report": state.diagnostic_report or {"message": "No failures."}}
    except Exception as e: return {"status": "error", "message": str(e)}

@app.get("/api/causal/{trace_id}")
async def get_causal_chain(trace_id: str):
    with db.get_connection() as conn:
        rows = conn.execute("SELECT event_id, causal_parent FROM events WHERE trace_id = ?", (trace_id,)).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/traces")
async def list_traces(limit: int = 50):
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM traces ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

@app.get("/api/arm/tasks")
async def list_pending_tasks():
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM task_queue WHERE status = 'PENDING'").fetchall()
        return [dict(row) for row in rows]

@app.post("/api/arm/execute/{task_id}")
async def arm_execute_task(task_id: str, background_tasks: BackgroundTasks):
    from clide import task_queue as queue
    from apc import executor
    with db.get_connection() as conn:
        task = conn.execute("SELECT * FROM task_queue WHERE task_id = ? AND status = 'PENDING'", (task_id,)).fetchone()
        if not task: return {"status": "error", "message": "Not found"}
    payload = json.loads(task["action_payload"])
    def run_manual():
        with db.get_connection() as conn:
            conn.execute("UPDATE task_queue SET status = 'CLAIMED', node_id = 'MANUAL_ARM' WHERE task_id = ?", (task_id,))
            conn.commit()
        res = executor.execute_command(task["trace_id"], payload.get("command"), task["causal_parent"])
        queue.complete_task(task_id, success=(res["exit_code"] == 0))
    background_tasks.add_task(run_manual)
    return {"status": "success"}

class SpoofRequest(pydantic.BaseModel):
    stdout: str
    stderr: str
    exit_code: int

@app.post("/api/arm/spoof/{task_id}")
async def arm_spoof_task(task_id: str, req: SpoofRequest):
    from clide import task_queue as queue
    with db.get_connection() as conn:
        task = conn.execute("SELECT * FROM task_queue WHERE task_id = ? AND status = 'PENDING'", (task_id,)).fetchone()
        if not task: return {"status": "error", "message": "Not found"}
        syscalls.cap_event_commit(trace_id=task["trace_id"], layer=syscalls.Layer.APC, event_type=syscalls.EventType.EXEC_COMPLETE,
            payload={"stdout": req.stdout, "stderr": req.stderr, "exit_code": req.exit_code, "manual_spoof": True}, causal_parent=task["causal_parent"])
        queue.complete_task(task_id, success=(req.exit_code == 0))
    return {"status": "success"}

@app.get("/api/swarm/agents")
async def get_agents():
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    if not os.path.exists(swarm_db): return []
    try:
        with sqlite3.connect(swarm_db) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM agent_wallets").fetchall()
            return [dict(row) for row in rows]
    except: return []

@app.get("/api/swarm/agent/{agent_id}")
async def get_agent_details(agent_id: str):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.row_factory = sqlite3.Row
        agent = conn.execute("SELECT * FROM agent_wallets WHERE agent_id = ?", (agent_id,)).fetchone()
        intents = conn.execute("SELECT * FROM intents WHERE owner_agent_id = ?", (agent_id,)).fetchall()
        return {"agent": dict(agent) if agent else None, "owned_intents": [dict(i) for i in intents]}

@app.get("/api/intents")
async def list_intents():
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    if not os.path.exists(swarm_db): return []
    with sqlite3.connect(swarm_db) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM intents ORDER BY price DESC").fetchall()]

class BuyRequest(pydantic.BaseModel):
    intent_id: int
    buyer_agent: str

@app.post("/api/intents/buy")
async def buy_intent(req: BuyRequest):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.row_factory = sqlite3.Row
        intent = conn.execute("SELECT * FROM intents WHERE id = ?", (req.intent_id,)).fetchone()
        buyer = conn.execute("SELECT balance FROM agent_wallets WHERE agent_id = ?", (req.buyer_agent,)).fetchone()
        if not intent or not buyer or buyer["balance"] < intent["price"]: return {"status": "error", "message": "Fail"}
        conn.execute("UPDATE agent_wallets SET balance = balance - ? WHERE agent_id = ?", (intent["price"], req.buyer_agent))
        conn.execute("UPDATE agent_wallets SET balance = balance + ? WHERE agent_id = ?", (intent["price"], intent["owner_agent_id"]))
        conn.execute("UPDATE intents SET owner_agent_id = ? WHERE id = ?", (req.buyer_agent, req.intent_id))
        conn.commit()
    return {"status": "success"}

class IntentCreateRequest(pydantic.BaseModel):
    name: str
    description: str
    price: float
    owner_agent_id: str
    actions: str = "[]"

@app.post("/api/intents/create")
async def create_intent(req: IntentCreateRequest):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.execute("INSERT INTO intents (name, description, actions, price, owner_agent_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                     (req.name, req.description, req.actions, req.price, req.owner_agent_id, int(time.time())))
        conn.commit()
    return {"status": "success"}

@app.delete("/api/intents/{intent_id}")
async def delete_intent(intent_id: int):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.execute("DELETE FROM intents WHERE id = ?", (intent_id,))
        conn.commit()
    return {"status": "success"}

# --- Swarm Messaging APIs ---
class SwarmMessage(pydantic.BaseModel):
    sender_id: str
    recipient_id: str
    message: str

@app.post("/api/swarm/message")
async def send_swarm_message(req: SwarmMessage):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.execute("INSERT INTO swarm_messages (sender_id, recipient_id, message, timestamp) VALUES (?, ?, ?, ?)",
                     (req.sender_id, req.recipient_id, req.message, int(time.time())))
        conn.commit()
    return {"status": "success"}

@app.get("/api/swarm/ledger")
async def get_ledger(agent_id: Optional[str] = None, limit: int = 100):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    if not os.path.exists(swarm_db): return []
    try:
        with sqlite3.connect(swarm_db) as conn:
            conn.row_factory = sqlite3.Row
            if agent_id:
                rows = conn.execute("SELECT * FROM credit_ledger WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?", (agent_id, limit)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM credit_ledger ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]
    except: return []

@app.get("/api/swarm/agent_stats/{agent_id}")
async def get_agent_stats(agent_id: str):
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    with sqlite3.connect(swarm_db) as conn:
        conn.row_factory = sqlite3.Row
        wallet = conn.execute("SELECT balance FROM agent_wallets WHERE agent_id = ?", (agent_id,)).fetchone()
        intents = conn.execute("SELECT count(*) as count FROM intents WHERE owner_agent_id = ?", (agent_id,)).fetchone()
        spent = conn.execute("SELECT SUM(amount) as total FROM credit_ledger WHERE agent_id = ? AND amount < 0", (agent_id,)).fetchone()
        earned = conn.execute("SELECT SUM(amount) as total FROM credit_ledger WHERE agent_id = ? AND amount > 0", (agent_id,)).fetchone()
        return {
            "balance": wallet["balance"] if wallet else 0,
            "intent_count": intents["count"] if intents else 0,
            "total_spent": abs(spent["total"] or 0),
            "total_earned": earned["total"] or 0
        }

# --- Testing APIs ---

@app.post("/api/test/burst")
async def trigger_diagnostic_burst():
    """Generates a complex web of synthetic traces and events for UI stress testing."""
    print("[*] TRIGGERING DIAGNOSTIC BURST...")
    
    # 1. Start a few parent traces
    parents = []
    goals = [
        "Optimize distributed kernel scheduling",
        "Refactor sovereign identity layer",
        "Prune stale episodic memory patterns",
        "Scale swarm compute capacity"
    ]
    
    for i in range(3):
        trace_id = syscalls.cap_trace_start()
        goal = random.choice(goals)
        syscalls.cap_event_commit(trace_id, syscalls.Layer.CLIDE, syscalls.EventType.GOAL_GENERATED, 
                                  {"goal": f"[DIAGNOSTIC] {goal}", "priority": random.random()})
        parents.append(trace_id)
        
    # 2. Add branching agent activity
    swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
    agents = ["prime"]
    if os.path.exists(swarm_db):
        with sqlite3.connect(swarm_db) as conn:
            rows = conn.execute("SELECT agent_id FROM agent_wallets LIMIT 5").fetchall()
            if rows: agents = [r[0] for r in rows]

    for p_id in parents:
        # Each trace gets 2-4 actions
        last_ev = None
        for j in range(random.randint(2, 4)):
            agent = random.choice(agents)
            # Simulate planning
            last_ev = syscalls.cap_event_commit(p_id, syscalls.Layer.PXE, syscalls.EventType.INFER,
                                               {"message": f"Agent {agent[:8]} planning next step", "confidence": random.random()},
                                               causal_parent=last_ev)
            # Simulate execution
            last_ev = syscalls.cap_event_commit(p_id, syscalls.Layer.APC, syscalls.EventType.EXEC_COMPLETE,
                                               {"command": f"test_cmd --unit {j}", "exit_code": 0, "stdout": "Test execution successful"},
                                               causal_parent=last_ev)
            
            # 10% chance of a child trace branch
            if random.random() < 0.1:
                child_id = syscalls.spawn_agent_trace(p_id, agent)
                syscalls.cap_event_commit(child_id, syscalls.Layer.APC, syscalls.EventType.EXEC_SPAWN,
                                         {"message": "Branching for sub-task"}, causal_parent=None)

    return {"status": "success", "message": f"Generated {len(parents)} synthetic trace trees"}

@app.post("/api/test/prune")
async def prune_diagnostic_traces():
    """Removes all synthetic traces and events created by the burst generator."""
    print("[*] PRUNING DIAGNOSTIC DATA...")
    try:
        with db.get_connection() as conn:
            # Find parent traces
            cursor = conn.execute("SELECT DISTINCT trace_id FROM events WHERE payload LIKE '%[DIAGNOSTIC]%'")
            parent_ids = [row[0] for row in cursor.fetchall()]
            
            # Include child traces (e.g., parent_id_agent_1234abcd)
            trace_ids = list(parent_ids)
            for p_id in parent_ids:
                cursor = conn.execute("SELECT DISTINCT trace_id FROM events WHERE trace_id LIKE ?", (f"{p_id}_agent_%",))
                trace_ids.extend([row[0] for row in cursor.fetchall()])
            
            if not trace_ids:
                return {"status": "success", "message": "No diagnostic traces found"}
            
            # Delete in chunks to avoid SQLite variable limits (999)
            for i in range(0, len(trace_ids), 900):
                chunk = trace_ids[i:i+900]
                placeholders = ",".join(["?"] * len(chunk))
                conn.execute(f"DELETE FROM events WHERE trace_id IN ({placeholders})", chunk)
                conn.execute(f"DELETE FROM traces WHERE trace_id IN ({placeholders})", chunk)
            
            conn.execute("DELETE FROM causal_index WHERE child_event_id NOT IN (SELECT event_id FROM events)")
            conn.execute("DELETE FROM causal_index WHERE parent_event_id NOT IN (SELECT event_id FROM events)")
            
            conn.commit()
            return {"status": "success", "message": f"Pruned {len(trace_ids)} diagnostic trace trees"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- File System IDE APIs ---
@app.get("/api/fs/ls")
async def fs_list(path: str = "."):
    base_path = PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(os.path.dirname(PROJECT_ROOT)): return {"status": "error", "message": "Access Denied"}
    try:
        items = []
        for item in os.listdir(full_path):
            ipath = os.path.join(full_path, item)
            items.append({"name": item, "is_dir": os.path.isdir(ipath), "path": os.path.relpath(ipath, base_path)})
        return {"items": items, "current_path": os.path.relpath(full_path, base_path)}
    except Exception as e: return {"status": "error", "message": str(e)}

@app.get("/api/fs/read")
async def fs_read(path: str):
    base_path = PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(os.path.dirname(PROJECT_ROOT)): return {"status": "error", "message": "Access Denied"}
    try:
        with open(full_path, "r") as f: return {"content": f.read()}
    except Exception as e: return {"status": "error", "message": str(e)}

class FileWriteRequest(pydantic.BaseModel):
    path: str
    content: str

@app.post("/api/fs/write")
async def fs_write(req: FileWriteRequest):
    base_path = PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base_path, req.path))
    if not full_path.startswith(os.path.dirname(PROJECT_ROOT)): return {"status": "error", "message": "Access Denied"}
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f: f.write(req.content)
        return {"status": "success"}
    except Exception as e: return {"status": "error", "message": str(e)}

class MkdirRequest(pydantic.BaseModel):
    path: str

@app.post("/api/fs/mkdir")
async def fs_mkdir(req: MkdirRequest):
    base_path = PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base_path, req.path))
    if not full_path.startswith(os.path.dirname(PROJECT_ROOT)): return {"status": "error", "message": "Access Denied"}
    try:
        os.makedirs(full_path, exist_ok=True)
        return {"status": "success"}
    except Exception as e: return {"status": "error", "message": str(e)}

class RenameRequest(pydantic.BaseModel):
    old_path: str
    new_path: str

@app.post("/api/fs/rename")
async def fs_rename(req: RenameRequest):
    base_path = PROJECT_ROOT
    old_full_path = os.path.normpath(os.path.join(base_path, req.old_path))
    new_full_path = os.path.normpath(os.path.join(base_path, req.new_path))
    if not old_full_path.startswith(os.path.dirname(PROJECT_ROOT)) or not new_full_path.startswith(os.path.dirname(PROJECT_ROOT)):
        return {"status": "error", "message": "Access Denied"}
    try:
        os.rename(old_full_path, new_full_path)
        return {"status": "success"}
    except Exception as e: return {"status": "error", "message": str(e)}

@app.delete("/api/fs/delete")
async def fs_delete(path: str):
    base_path = PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base_path, path))
    if not full_path.startswith(os.path.dirname(PROJECT_ROOT)): return {"status": "error", "message": "Access Denied"}
    try:
        if os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"status": "success"}
    except Exception as e: return {"status": "error", "message": str(e)}

# --- Observability APIs ---

@app.get("/api/observability/causal/{trace_id}")
async def get_causal_graph(trace_id: str):
    return graph_builder.build_causal_graph(trace_id)

@app.get("/api/observability/swarm/{trace_id}")
async def get_swarm_interaction(trace_id: str):
    return graph_builder.build_agent_interaction_graph(trace_id)

@app.get("/api/observability/full_mesh")
async def get_full_causal_mesh():
    """Returns every agent, trace, and event as a unified causal graph."""
    nodes = []
    links = []
    
    try:
        # 0. Subsystems (Core Nodes)
        core_nodes_added = False
        arch_model_path = os.path.join(DATA_DIR, "cap_arch_model.json")
        if os.path.exists(arch_model_path):
            try:
                with open(arch_model_path, "r") as f:
                    arch_data = json.load(f)
                    subsystems = arch_data.get("subsystems", {})
                    if subsystems:
                        for name, info in subsystems.items():
                            nodes.append({"id": name, "type": name, "label": name, "data": info.get("metrics", {})})
                        core_nodes_added = True
            except: pass
        
        # Fallback if no arch model file
        if not core_nodes_added:
            for name in ["CLIDE", "APC", "PIE"]:
                nodes.append({"id": name, "type": name, "label": name, "data": {}})

        # 1. Agents
        swarm_db = os.path.join(DATA_DIR, "cap_swarm.db")
        if os.path.exists(swarm_db):
            try:
                with sqlite3.connect(swarm_db) as conn:
                    conn.row_factory = sqlite3.Row
                    agents = conn.execute("SELECT * FROM agent_wallets").fetchall()
                    for a in agents:
                        nodes.append({"id": a["agent_id"], "type": "AGENT", "label": f"AGENT_{a['agent_id'][:8]}", "data": dict(a)})
                        links.append({"source": "CLIDE", "target": a["agent_id"], "type": "MANAGEMENT"})
            except: pass
        
        # 2. Events & Traces
        if os.path.exists(db.DB_PATH):
            try:
                with db.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    events = conn.execute("SELECT event_id, trace_id, layer, event_type, causal_parent, payload FROM events ORDER BY timestamp DESC LIMIT 500").fetchall()
                    for e in events:
                        label = e["event_type"]
                        if e["payload"]:
                            try:
                                p_data = json.loads(e["payload"]) if isinstance(e["payload"], str) else e["payload"]
                                if "goal" in p_data: label = f"GOAL: {p_data['goal'][:15]}..."
                                elif "command" in p_data: label = f"CMD: {p_data['command'][:15]}..."
                                elif "message" in p_data: label = f"MSG: {p_data['message'][:15]}..."
                            except: pass
                        
                        nodes.append({"id": e["event_id"], "type": "EVENT", "label": label, "data": {"layer": e["layer"]}})
                        if e["causal_parent"]:
                            links.append({"source": e["causal_parent"], "target": e["event_id"], "type": "CAUSAL"})
                        links.append({"source": e["trace_id"], "target": e["event_id"], "type": "TRACE_MEMBER"})
                        
                    traces = conn.execute("SELECT trace_id FROM events GROUP BY trace_id ORDER BY timestamp DESC LIMIT 50").fetchall()
                    for t in traces:
                         trace_label = f"TRACE_{t['trace_id'][:8]}"
                         goal_event = conn.execute("SELECT payload FROM events WHERE trace_id = ? AND event_type = 'GOAL_GENERATED' LIMIT 1", (t["trace_id"],)).fetchone()
                         if goal_event and goal_event["payload"]:
                             try:
                                 p_data = json.loads(goal_event["payload"]) if isinstance(goal_event["payload"], str) else goal_event["payload"]
                                 if "goal" in p_data:
                                     trace_label = f"🧵 {p_data['goal'][:20]}..."
                             except: pass
                         
                         nodes.append({"id": t["trace_id"], "type": "TRACE", "label": trace_label})
                         links.append({"source": "CLIDE", "target": t["trace_id"], "type": "ORCHESTRATION"})
            except Exception as e: print(f"DB Error: {e}")

    except Exception as e:
        print(f"[!] Mesh Extraction Error: {e}")
        
    return {"nodes": nodes, "links": links}

@app.get("/api/observability/state/{trace_id}")
async def get_cognitive_state(trace_id: str):
    builder = StateBuilder(trace_id=trace_id)
    builder.rebuild_from_db(trace_id)
    return builder.get_snapshot()

@app.get("/api/observability/intent")
async def get_system_intent():
    """Returns dominant goals and current strategies."""
    main_goal = goal_manager.get_highest_priority_goal()
    return {
        "active_goal": main_goal.dict() if main_goal else None,
        "active_goals_count": len(goal_manager.active_goals),
        "system_status": "OPERATIONAL"
    }

# --- Control APIs ---

class ControlCommandRequest(pydantic.BaseModel):
    action: str
    target_id: str
    payload: Dict[str, Any] = {}
    trace_id: Optional[str] = None

@app.post("/api/control/command")
async def execute_control_command(req: ControlCommandRequest):
    try:
        action = ActionType(req.action)
        res = control_router.handle_command(action, req.target_id, req.payload, req.trace_id)
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/control/goal")
async def inject_system_goal(req: GoalRequest):
    payload = {"goal": req.goal, "priority": 0.8} # Default priority
    res = control_router.handle_command(ActionType.INJECT_GOAL, "system", payload)
    if res["status"] == "success":
         goal_id = goal_manager.inject_goal(req.goal, priority=0.8)
         return {"status": "success", "goal_id": goal_id}
    return res

# --- WebSocket for Real-Time Telemetry ---
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[*] WS: Connected.")
    
    async def send_to_client(message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except:
            pass # Socket might be closed
            
    stream_processor.subscribe(send_to_client)
    
    try:
        while True:
            await asyncio.sleep(10) # Keep connection alive
    except Exception as e: print(f"[*] WS: Error: {e}")

@app.websocket("/ws/subsystem/{subsystem_id}")
async def subsystem_websocket_endpoint(websocket: WebSocket, subsystem_id: str):
    await subsystem_manager.connect(websocket, subsystem_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        subsystem_manager.disconnect(websocket, subsystem_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
