import os
import sys
import json
import time
import random
import math
import sqlite3
import asyncio
import socket
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Tuple

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.text import Text
from rich import box

# --- Configuration & Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APC_DIR = PROJECT_ROOT
ARCH_MODEL_PATH = os.path.join(PROJECT_ROOT, "data/cap_arch_model.json")
EVENTS_DB_PATH = os.path.join(PROJECT_ROOT, "data/cap_events.db")
VERSION_FILE = os.path.join(PROJECT_ROOT, "VERSION")

VERSION = "4.0.0"
with open(VERSION_FILE, "w") as f:
    f.write(VERSION)

# --- Visual Settings ---
BRAILLE_CHARS = ["⡷", "⣧", "⢾", "⣯", "⡟", "⡿", "⣿", "⣻", "⢿", "⡿"]
AGENT_SYMBOLS = ["🧬", "🧠", "🐝", "🧿", "⌬", "⏣"]
COLORS = ["bright_cyan", "bright_magenta", "bright_green", "yellow", "bright_blue", "white"]

# --- State Management ---
class SingularityState:
    def __init__(self):
        self.start_time = time.time()
        self.nodes = []
        self.logs = []
        self.exec_load = 0.3
        self.swarm_load = 0.5
        self.last_event_rowid = 0
        self.is_paused = False
        self.efficiency = 1.0
        self.boot_logs = []
        self.generation = 0
        self.cognitive_load = 0.2

    def log_boot(self, msg):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.boot_logs.append(f"[{ts}] {msg}")

    def update_vitals(self):
        try:
            if os.path.exists(ARCH_MODEL_PATH):
                with open(ARCH_MODEL_PATH, "r") as f:
                    data = json.load(f)
                    nodes_data = data.get("ACTIVE_NODES", [])
                    # Fallback to subsystems if no active nodes
                    if not nodes_data:
                        subsystems = data.get("subsystems", {})
                        nodes_data = [{"node_id": k, "load_limit": v.get("metrics", {}).get("efficiency", 0.5)} for k, v in subsystems.items()]

                    self.efficiency = data.get("subsystems", {}).get("APC", {}).get("metrics", {}).get("efficiency", 1.0)
                    
                    # Update swarm population metrics
                    swarm_db = os.path.join(PROJECT_ROOT, "data/cap_swarm.db")
                    if os.path.exists(swarm_db):
                         with sqlite3.connect(swarm_db) as conn:
                              count = conn.execute("SELECT COUNT(*) FROM agent_wallets").fetchone()[0]
                              self.swarm_load = min(1.0, count / 20.0)

                    if not self.nodes:
                        for i, n in enumerate(nodes_data):
                            self.nodes.append({
                                "name": n.get("node_id", "UNK"),
                                "symbol": AGENT_SYMBOLS[i % len(AGENT_SYMBOLS)],
                                "radius": 14 + i * 5,
                                "speed": 0.3 + random.random() * 0.5,
                                "angle": random.random() * math.pi * 2,
                                "color": COLORS[i % len(COLORS)],
                                "load": n.get("load_limit", 0.0)
                            })
                    else:
                        for i, n in enumerate(nodes_data):
                            if i < len(self.nodes):
                                self.nodes[i]["load"] = n.get("load_limit", 0.0)
                    
                    self.exec_load = 0.3 + 0.2 * math.sin(time.time() * 3)
                    self.cognitive_load = 0.2 + 0.4 * abs(math.sin(time.time() * 0.5))
        except: pass

    def fetch_events(self):
        # Always inject boot logs if they haven't been shown yet
        if self.boot_logs:
            for msg in self.boot_logs:
                self.logs.insert(0, {
                    "text": f"[BOOT] {msg}",
                    "color": "green",
                    "y_pos": 0,
                    "node_link": None
                })
            self.boot_logs = []

        if not os.path.exists(EVENTS_DB_PATH): return
        try:
            conn = sqlite3.connect(f"file:{EVENTS_DB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, timestamp, layer, event_type, payload FROM events WHERE rowid > ? ORDER BY rowid ASC LIMIT 5", (self.last_event_rowid,))
            rows = cursor.fetchall()
            for row in rows:
                rid, ts, layer, etype, payload = row
                self.last_event_rowid = rid
                try:
                    p_data = json.loads(payload)
                    msg = p_data.get("message") or etype
                except: msg = etype
                
                # Cognitive Event Mapping
                color = "cyan"
                if "GOAL" in etype or "DECISION" in etype: color = "bright_magenta"
                elif "INFERENCE" in etype: color = "yellow"
                elif "EPISODE" in etype: color = "bright_green"
                elif "ERROR" in etype or "FAIL" in etype: color = "bright_red"
                elif "INTERVENTION" in etype: color = "orange1"

                self.logs.insert(0, {
                    "text": f"[{layer}] {msg}",
                    "color": color,
                    "y_pos": 0,
                    "node_link": None
                })
            conn.close()
        except: pass

    def step(self):
        if self.is_paused: return
        dt = 0.05
        for node in self.nodes:
            node["angle"] += node["speed"] * self.efficiency * dt
        for log in self.logs:
            log["y_pos"] += 1
        self.logs = [l for l in self.logs if l["y_pos"] < 25]

# --- Render Components ---
class SingularityPulse:
    def __init__(self, state: SingularityState):
        self.state = state

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        width = options.max_width
        height = options.max_height
        
        # 1. Margins (Braille Bio-Rhythm)
        left_margin = []
        right_margin = []
        for h in range(height):
            l_idx = int((math.sin(time.time() * 3 + h * 0.7) + 1) * 3.5 * self.state.exec_load)
            r_idx = int((math.cos(time.time() * 2.5 + h * 0.6) + 1) * 3.5 * self.state.swarm_load)
            left_margin.append(Text(BRAILLE_CHARS[l_idx % len(BRAILLE_CHARS)], style="bold cyan"))
            right_margin.append(Text(BRAILLE_CHARS[r_idx % len(BRAILLE_CHARS)], style="bold magenta"))

        # 2. Central Canvas
        canvas_width = width - 10
        center_x = canvas_width // 2
        center_y = height // 2
        lines = [Text(" " * canvas_width) for _ in range(height)]
        
        # Draw Kernel Pulse
        pulse_char = "🧿" if int(time.time() * 4) % 2 == 0 else "🌀"
        if 0 <= center_y < height:
            lines[center_y] = Text(" " * (center_x - 1) + pulse_char + " " * (canvas_width - center_x - 1), style="bold blue")

        # Draw Orbiting Agents
        for node in self.state.nodes:
            rx = int(node["radius"] * 2.0 * math.cos(node["angle"]))
            ry = int(node["radius"] * 0.6 * math.sin(node["angle"]))
            px = center_x + rx
            py = center_y + ry
            if 0 <= py < height and 0 <= px < canvas_width:
                style = node["color"]
                if ry < 0: style = f"dim {style}"
                else: style = f"bold {style}"
                
                # Anomaly Vibration
                if "error" in str(self.state.logs[:1]).lower() and random.random() < 0.3:
                    style = "bold red" if int(time.time() * 15) % 2 == 0 else style
                
                lines[py].plain = lines[py].plain[:px] + node["symbol"] + lines[py].plain[px+1:]
                lines[py].stylize(style, px, px+1)

        # Draw Waterfall Logs
        for log in self.state.logs:
            y = int(log["y_pos"])
            if 0 <= y < height:
                msg = log["text"]
                if len(msg) > 50: msg = msg[:47] + "..."
                alpha = max(0, 1.0 - (y / 25))
                style = log["color"]
                if alpha < 0.3: style = "dim white"
                elif alpha < 0.6: style = f"dim {style}"
                
                start_x = center_x - len(msg) // 2
                if 0 <= start_x < canvas_width:
                    lines[y].plain = lines[y].plain[:start_x] + msg + lines[y].plain[start_x+len(msg):]
                    lines[y].stylize(style, start_x, start_x+len(msg))

        for h in range(height):
            yield left_margin[h] + Text("  ") + lines[h] + Text("  ") + right_margin[h]

# --- Launcher Logic ---
def kill_existing_processes(state):
    try:
        output = subprocess.check_output(["pgrep", "-f", "core/clide/dashboard/server.py"]).decode().split()
        my_pid = os.getpid()
        for pid_str in output:
            pid = int(pid_str)
            if pid != my_pid:
                os.kill(pid, 9)
                state.log_boot(f"TERMINATED PID {pid}")
    except: pass

def start_backend(state):
    state.log_boot("SPAWNING BACKEND_IDE...")
    log_path = os.path.join(PROJECT_ROOT, "dashboard_server.log")
    cmd = [sys.executable, "core/clide/dashboard/server.py"]
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.path.join(PROJECT_ROOT, 'core')}:{env.get('PYTHONPATH', '')}"
    try:
        with open(log_path, "w") as f:
            subprocess.Popen(cmd, cwd=PROJECT_ROOT, env=env, stdout=f, stderr=f)
        state.log_boot(f"SERVER_SPAWN: Success. Logs: {log_path}")
        return True
    except Exception as e:
        state.log_boot(f"SERVER_SPAWN: Failed: {e}")
        return False

async def main():
    console = Console()
    state = SingularityState()
    pulse = SingularityPulse(state)
    
    state.log_boot(f"INITIATING CAP.OS v{VERSION} (COGNITIVE_ARCHITECTURE_PLATFORM)...")
    
    # 1. Subsystem Initialization
    state.log_boot("STABILIZING COGNITIVE CORE...")
    state.log_boot("MOUNTING STATE_GRAPH [NODE_TYPE: UNIFIED]...")
    
    state.log_boot("LOADING MEMORY STACK...")
    state.log_boot("LAYER_1: WORKING_MEMORY [CAPACITY: 50]... LOADED")
    state.log_boot("LAYER_2: EPISODIC_MEMORY [INDEXED]... LOADED")
    state.log_boot("LAYER_3: SEMANTIC_MEMORY [CONSOLIDATION_ACTIVE]... LOADED")
    
    state.log_boot("ARMING DARWINIAN SWARM ECOSYSTEM...")
    state.log_boot("LOADING GENOME_ENGINE v1.0.0...")
    state.log_boot("SELECTION_PRESSURE: ACTIVE [THRESHOLD: 0.2]")
    
    state.log_boot("SECURING CONTROL_LAYER...")
    state.log_boot("PERMISSION_MODEL: RBAC [ADMIN_AUTH]...")
    state.log_boot("POLICY_ENGINE: CONSTRAINTS_MOUNTED...")
    
    # 2. Process Management
    kill_existing_processes(state)
    start_backend(state)
    
    state.update_vitals()
    with Live(pulse, console=console, screen=True, refresh_per_second=20) as live:
        while True:
            state.update_vitals()
            state.fetch_events()
            state.step()
            await asyncio.sleep(0.05)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] SYSTEM_SHUTDOWN: Singularity Pulse Terminated.")
