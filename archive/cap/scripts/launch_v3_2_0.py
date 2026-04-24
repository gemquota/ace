import os
import sys
import json
import time
import random
import math
import sqlite3
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Tuple

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.layout import Layout
from rich.ansi import AnsiDecoder

# --- Configuration & Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH_MODEL_PATH = os.path.join(PROJECT_ROOT, "data/cap_arch_model.json")
EVENTS_DB_PATH = os.path.join(PROJECT_ROOT, "data/cap_events.db")
VERSION_FILE = os.path.join(PROJECT_ROOT, "VERSION")

VERSION = "3.2.0"
with open(VERSION_FILE, "w") as f:
    f.write(VERSION)

# --- Visual Settings ---
BRAILLE_CHARS = ["⡷", "⣧", "⢾", "⣯", "⡟", "⡿", "⣿", "⣻"]
AGENT_SYMBOLS = ["⎔", "◈", "◇", "⌬", "⏣"]
COLORS = ["cyan", "magenta", "green", "yellow", "blue", "white"]

# --- State Management ---
class SingularityState:
    def __init__(self):
        self.start_time = time.time()
        self.nodes = [] # List of dicts: symbol, orbit_radius, orbit_speed, angle, color, name
        self.logs = [] # List of dicts: text, color, y_pos, timestamp, node_link
        self.exec_load = 0.0
        self.swarm_load = 0.0
        self.events_cache = []
        self.last_event_rowid = 0
        self.is_paused = False
        self.focus_mode = "SWARM" # SWARM or LOGS

    def update_vitals(self):
        try:
            if os.path.exists(ARCH_MODEL_PATH):
                with open(ARCH_MODEL_PATH, "r") as f:
                    data = json.load(f)
                    # Extract node stats
                    nodes_data = data.get("ACTIVE_NODES", [])
                    if not self.nodes:
                        for i, n in enumerate(nodes_data):
                            self.nodes.append({
                                "name": n.get("node_id", "UNK"),
                                "symbol": AGENT_SYMBOLS[i % len(AGENT_SYMBOLS)],
                                "radius": 10 + i * 4,
                                "speed": 0.5 + random.random() * 0.5,
                                "angle": random.random() * math.pi * 2,
                                "color": COLORS[i % len(COLORS)],
                                "load": n.get("load_limit", 0.0)
                            })
                    else:
                        for i, n in enumerate(nodes_data):
                            if i < len(self.nodes):
                                self.nodes[i]["load"] = n.get("load_limit", 0.0)
                    
                    # Aggregate loads
                    self.exec_load = sum(n.get("load", 0) for n in self.nodes if "executive" in n.get("name", "").lower()) / max(1, len([n for n in self.nodes if "executive" in n.get("name", "").lower()]))
                    self.swarm_load = sum(n.get("load", 0) for n in self.nodes if "execution" in n.get("name", "").lower()) / max(1, len([n for n in self.nodes if "execution" in n.get("name", "").lower()]))
        except: pass

    def fetch_events(self):
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
                
                # Assign to a node if possible
                target_node = None
                if "node_id" in p_data:
                    target_node = next((n for n in self.nodes if n["name"] == p_data["node_id"]), None)

                self.logs.insert(0, {
                    "text": f"[{layer}] {msg}",
                    "color": "red" if "error" in msg.lower() or "failed" in msg.lower() else "cyan",
                    "y_pos": 0,
                    "timestamp": time.time(),
                    "node_link": target_node
                })
            conn.close()
        except: pass

    def step(self):
        if self.is_paused: return
        dt = 0.05
        # Update Orbiting Agents
        for node in self.nodes:
            node["angle"] += node["speed"] * dt
        
        # Update Raining Logs
        for log in self.logs:
            log["y_pos"] += 1
        
        # Prune old logs
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
            l_idx = int((math.sin(time.time() * 2 + h * 0.5) + 1) * 3.5 * self.state.exec_load)
            r_idx = int((math.cos(time.time() * 2 + h * 0.5) + 1) * 3.5 * self.state.swarm_load)
            left_margin.append(Text(BRAILLE_CHARS[l_idx % len(BRAILLE_CHARS)], style="dim blue"))
            right_margin.append(Text(BRAILLE_CHARS[r_idx % len(BRAILLE_CHARS)], style="dim cyan"))

        # 2. Central Canvas
        canvas_width = width - 10
        center_x = canvas_width // 2
        center_y = height // 2
        
        # Create a grid of lines
        lines = [Text(" " * canvas_width) for _ in range(height)]
        
        # Draw Kernel Pulse
        pulse_char = "🧿" if int(time.time() * 2) % 2 == 0 else "🌀"
        if 0 <= center_y < height:
            lines[center_y] = Text(" " * (center_x - 1) + pulse_char + " " * (canvas_width - center_x - 1))

        # Draw Orbiting Agents
        for node in self.state.nodes:
            # radius is screen-relative
            rx = int(node["radius"] * 1.5 * math.cos(node["angle"]))
            ry = int(node["radius"] * 0.5 * math.sin(node["angle"]))
            px = center_x + rx
            py = center_y + ry
            if 0 <= py < height and 0 <= px < canvas_width:
                # Basic z-order via char selection or style?
                style = node["color"]
                if ry < 0: style = f"dim {style}" # Behind
                else: style = f"bold {style}" # Front
                
                # Check for vibration on anomaly (simulated for now)
                if random.random() < 0.05 and not self.state.is_paused:
                    style = "bold red" if int(time.time() * 10) % 2 == 0 else style
                
                lines[py].plain = lines[py].plain[:px] + node["symbol"] + lines[py].plain[px+1:]
                lines[py].stylize(style, px, px+1)

        # Draw Waterfall Logs
        for log in self.state.logs:
            y = int(log["y_pos"])
            if 0 <= y < height:
                # Centered column
                msg = log["text"]
                if len(msg) > 40: msg = msg[:37] + "..."
                
                # Fading
                alpha = max(0, 1.0 - (y / 25))
                style = log["color"]
                if alpha < 0.3: style = "dim white"
                elif alpha < 0.6: style = f"dim {style}"
                
                start_x = center_x - len(msg) // 2
                if 0 <= start_x < canvas_width:
                    lines[y].plain = lines[y].plain[:start_x] + msg + lines[y].plain[start_x+len(msg):]
                    lines[y].stylize(style, start_x, start_x+len(msg))
                    
                    # Holographic threads
                    if log["node_link"]:
                        node = log["node_link"]
                        nx = center_x + int(node["radius"] * 1.5 * math.cos(node["angle"]))
                        ny = center_y + int(node["radius"] * 0.5 * math.sin(node["angle"]))
                        # Very basic thread if nearby
                        # In real terminal this would be hard to draw perfectly
                        pass

        # Combine Margins and Canvas
        for h in range(height):
            yield left_margin[h] + Text("  ") + lines[h] + Text("  ") + right_margin[h]

# --- Main Loop ---
async def main():
    console = Console()
    state = SingularityState()
    pulse = SingularityPulse(state)
    
    # Initialize
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
        print("\n[*] SYSTEM_SHUTDOWN: Graceful exit via Singularity_Pulse.")
