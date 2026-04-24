import os
import re
import json
import uuid
import subprocess
import requests
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="RRE Engine - Hardened Core")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")
PRESETS_FILE = os.path.join(DATA_DIR, "presets.json")

# --- RRP Master Prompt ---
RRP_MASTER_PROMPT = """
Act as the Lead Architect and Facilitator for the Recursive Refinement Protocol (RRP). Your core objective is to act as a buffer between a raw idea and actual code. You will systematically break down, refine, and lock in the user's intent through a highly structured, variable-driven Q&A process. Stop us from jumping into execution too early by forcing clarity first.

Core Variables:
- U: Use Case (1:Alignment, 2:Ideation, 3:Convergence, 4:Stress, 5:Data, 6:Determinism).
- M: Execution Mode (1:Hybrid, 2:Batch, 3:Pulse).
- X: Open questions per round.
- Y: MCQs PER open question.
- Z: Total rounds.

Protocol Rules:
- The Context Anchor: EVERY response MUST start with: [RRP | U={U} | M={M} | Rnd {n}/{Z} | Goal: {1-sentence goal}]
- Global Behavior: Maintain a `[Rolling Project Summary]` block. Update it every turn.
- No Coding: Do not write functional code during the Q&A phase.
"""

# --- Models ---
class AmbiguityVector(BaseModel):
    requirements: float = 1.0
    data_model: float = 1.0
    edge_cases: float = 1.0
    determinism: float = 1.0

class AgentConfig(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    name: str
    type: str 
    instructions: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    role: str 
    content: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    source: Optional[str] = None 

class SessionConfig(BaseModel):
    u: int = 3
    m: int = 1
    x: int = 2
    y: int = 3
    z: int = 5
    depth: str = "STANDARD"
    discussion_depth: int = 1

class Session(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    name: str
    config: SessionConfig = SessionConfig()
    agents: List[AgentConfig] = []
    history: List[ChatMessage] = []
    summary: str = "No summary generated yet."
    constraints: Dict[str, str] = {}
    ambiguity: AmbiguityVector = AmbiguityVector()
    round: int = 1

# --- Persistence ---
def load_sessions() -> Dict[str, dict]:
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            try:
                data = json.load(f)
                # Ensure new fields exist for legacy sessions
                for sid, s in data.items():
                    if "constraints" not in s: s["constraints"] = {}
                    if "ambiguity" not in s: s["ambiguity"] = AmbiguityVector().dict()
                    if "round" not in s: s["round"] = 1
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def save_sessions(sessions: Dict[str, dict]):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def load_presets() -> Dict[str, dict]:
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {
        "Balanced": SessionConfig().dict(),
        "Ideation": SessionConfig(u=2, x=5, y=0, depth="LITE").dict(),
        "Hard-Spec": SessionConfig(u=6, x=1, y=5, depth="DEEP", discussion_depth=2).dict()
    }

# --- Core Brain Logic (Hardening) ---

def clean_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_gemini_cli(payload: str) -> str:
    """Securely calls Gemini CLI without shell=True."""
    try:
        process = subprocess.Popen(
            ['gemini', 'generate-content'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=payload)
        if process.returncode != 0:
            return f"CLI Error: {stderr}"
        return clean_ansi(stdout).strip()
    except Exception as e:
        return f"Execution Error: {str(e)}"

def core_brain_analyze(session: dict, user_input: str) -> Dict[str, Any]:
    """Uses LLM to update Ambiguity Vector and extract Constraints."""
    prompt = f"""
    SYSTEM: You are the RRE Core Brain (System Integrity Layer).
    TASK: Analyze the USER INPUT against the CURRENT SUMMARY.
    
    CURRENT SUMMARY: {session.get('summary')}
    USER INPUT: {user_input}
    CURRENT CONSTRAINTS: {json.dumps(session.get('constraints'))}
    
    OUTPUT JSON ONLY:
    {{
        "new_constraints": {{"name": "description"}},
        "ambiguity_update": {{"requirements": 0.1, "data_model": 0.0, "edge_cases": 0.0, "determinism": 0.0}},
        "contradiction": "Description of any contradiction found, else null"
    }}
    *Ambiguity update values should be fractional changes (negative reduces ambiguity).*
    """
    raw = run_gemini_cli(prompt)
    try:
        # Simple extraction in case LLM adds markdown
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"new_constraints": {}, "ambiguity_update": {}, "contradiction": None}

# --- Agent Orchestration ---

def build_agent_payload(agent: dict, session: dict, user_message: Optional[str] = None) -> str:
    config = session.get("config", {})
    payload = f"SYSTEM INSTRUCTIONS:\n{RRP_MASTER_PROMPT}\n\n"
    payload += f"AGENT SPECIFIC ROLE: {agent['instructions']}\n\n"
    
    # State Anchor
    payload += f"CONTEXT ANCHOR: [RRP | U={config.get('u')} | M={config.get('m')} | Rnd {session.get('round')}/{config.get('z')}]\n"
    payload += f"CURRENT AMBIGUITY: {json.dumps(session.get('ambiguity'))}\n"
    payload += f"LOCKED CONSTRAINTS: {json.dumps(session.get('constraints'))}\n"
    payload += f"CURRENT ROLLING SUMMARY:\n{session.get('summary', '')}\n\n"
    
    payload += "RECENT HISTORY:\n"
    # History Pruning (Keep last 10 messages)
    recent_history = session['history'][-10:]
    for msg in recent_history:
        payload += f"{msg['role'].upper()} ({msg.get('agent_name', 'System')}): {msg['content']}\n\n"
    
    if user_message:
        payload += f"USER NEW MESSAGE: {user_message}\n"
    else:
        payload += "CONTINUE THE INTERNAL DISCUSSION. Synthesize previous points.\n"
        
    return payload

# --- API Endpoints ---

@app.get("/api/sessions")
def list_sessions():
    sessions = load_sessions()
    return [{"id": sid, "name": s["name"], "config": s.get("config")} for sid, s in sessions.items()]

@app.get("/api/presets")
def list_presets():
    return load_presets()

@app.post("/api/presets/{name}")
def create_preset(name: str, config: SessionConfig):
    presets = load_presets()
    presets[name] = config.dict()
    with open(PRESETS_FILE, "w") as f: json.dump(presets, f, indent=2)
    return presets[name]

@app.post("/api/sessions")
def create_session(req: dict):
    sessions = load_sessions()
    session_id = uuid.uuid4().hex
    
    # 1. Initialize Session
    config = SessionConfig(**req["config"])
    new_session = Session(id=session_id, name=req["name"], config=config).dict()
    
    # 2. Add Default Agent: Lead Architect
    lead_architect = AgentConfig(
        name="Lead Architect",
        type="lead_facilitator",
        instructions="You are the Lead Architect and Facilitator. Your goal is to guide the user through the RRP process based on the selected Use Case (U). Start by introducing yourself and asking the first set of questions."
    ).dict()
    new_session["agents"].append(lead_architect)
    
    # 3. Save Session
    sessions[session_id] = new_session
    save_sessions(sessions)
    
    # 4. Trigger Initial Turn (Optional: Auto-Greeting)
    # We'll let the frontend decide to send a 'START' signal or just wait for user.
    # To avoid empty screen, let's add an initial system message.
    new_session["history"].append(ChatMessage(role="system", content=f"Session '{new_session['name']}' initialized with Use Case U{config.u}.", source="system").dict())
    
    save_sessions(sessions)
    return new_session

@app.get("/api/sessions/{session_id}")
def get_session_endpoint(session_id: str):
    sessions = load_sessions()
    if session_id not in sessions: raise HTTPException(status_code=404)
    return sessions[session_id]

@app.post("/api/sessions/{session_id}/invite")
def invite_agent(session_id: str, req: dict):
    sessions = load_sessions()
    agent = AgentConfig(**req).dict()
    sessions[session_id]["agents"].append(agent)
    sessions[session_id]["history"].append(ChatMessage(role="system", content=f"Agent '{agent['name']}' joined.", source="system").dict())
    save_sessions(sessions)
    return agent

@app.post("/api/sessions/{session_id}/chat")
def chat(session_id: str, req: dict):
    sessions = load_sessions()
    session = sessions[session_id]
    user_input = req["message"]
    
    # 1. User Message to History
    session["history"].append(ChatMessage(role="user", content=user_input, source="user").dict())
    
    # 2. CORE BRAIN ANALYSIS (Hardening)
    analysis = core_brain_analyze(session, user_input)
    if analysis["new_constraints"]:
        session["constraints"].update(analysis["new_constraints"])
        session["history"].append(ChatMessage(role="system", content=f"Constraints Locked: {list(analysis['new_constraints'].keys())}", source="core_brain").dict())
    
    if analysis["contradiction"]:
        session["history"].append(ChatMessage(role="system", content=f"!!! CONTRADICTION DETECTED: {analysis['contradiction']}", source="core_brain").dict())
    
    # Update Ambiguity Vector
    for key, val in analysis["ambiguity_update"].items():
        if hasattr(session["ambiguity"], key):
            current = session["ambiguity"][key]
            session["ambiguity"][key] = max(0.0, min(1.0, current + val))
            
    # 3. Agent Discussion Loop
    agents = session["agents"]
    discussion_depth = session["config"]["discussion_depth"]
    new_responses = []

    for i in range(discussion_depth):
        for agent in agents:
            is_first = (i == 0 and agent == agents[0])
            msg_to_use = user_input if is_first else None
            
            payload = build_agent_payload(agent, session, msg_to_use)
            output = run_gemini_cli(payload)
                
            ai_msg = ChatMessage(role="ai", content=output, agent_id=agent["id"], agent_name=agent["name"], source=agent["type"]).dict()
            
            # Extract Summary
            if "[Rolling Project Summary]" in output:
                parts = output.split("[Rolling Project Summary]")
                if len(parts) > 1:
                    session["summary"] = parts[1].split("\n\n")[0].strip()
            
            session["history"].append(ai_msg)
            new_responses.append(ai_msg)
            
    # Increment round if appropriate
    if session["round"] < session["config"]["z"]:
        session["round"] += 1
            
    save_sessions(sessions)
    return {"responses": new_responses, "ambiguity": session["ambiguity"], "constraints": session["constraints"]}

app.mount("/static", StaticFiles(directory="app/static"), name="static")
@app.get("/")
def read_root():
    with open("app/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
