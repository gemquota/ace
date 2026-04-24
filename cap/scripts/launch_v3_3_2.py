import os
import sys
import json
import time
import sqlite3
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Tuple

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align
from rich.layout import Layout

# --- Configuration & Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH_MODEL_PATH = os.path.join(PROJECT_ROOT, "data/cap_arch_model.json")
EVENTS_DB_PATH = os.path.join(PROJECT_ROOT, "data/cap_events.db")
VERSION_FILE = os.path.join(PROJECT_ROOT, "VERSION")

VERSION = "3.3.2"
with open(VERSION_FILE, "w") as f:
    f.write(VERSION)

# --- ASCII Banner ---
BANNER = r"""
 ██████╗ █████╗ ██████╗      ██████╗ ███████╗
██╔════╝██╔══██╗██╔══██╗    ██╔═══██╗██╔════╝
██║     ███████║██████╔╝    ██║   ██║███████╗
██║     ██╔══██║██╔═══╝     ██║   ██║╚════██║
╚██████╗██║  ██║██║         ╚██████╔╝███████║
 ╚═════╝╚═╝  ╚═╝╚═╝          ╚═════╝ ╚══════╝
      SINGULARITY_PULSE // V3.3.2
"""

# --- State Management ---
class BrutalState:
    def __init__(self):
        self.nodes = []
        self.logs = []
        self.exec_vitals = {"uptime": "0s", "credits": "0.00", "version": VERSION}
        self.last_event_rowid = 0
        self.start_time = time.time()

    def update_vitals(self):
        try:
            if os.path.exists(ARCH_MODEL_PATH):
                with open(ARCH_MODEL_PATH, "r") as f:
                    data = json.load(f)
                    self.nodes = data.get("ACTIVE_NODES", [])
            
            uptime_sec = int(time.time() - self.start_time)
            self.exec_vitals["uptime"] = f"{uptime_sec}s"
            # In a real system, we'd fetch actual credits from a DB
            self.exec_vitals["credits"] = f"{12450.22 + (uptime_sec * 0.01):.2f}"
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
                
                dt = datetime.fromtimestamp(ts/1000).strftime('%H:%M:%S')
                status = "[ FAIL ]" if "error" in msg.lower() or "failed" in msg.lower() else "[  OK  ]"
                color = "bold red" if status == "[ FAIL ]" else "bold green"
                
                self.logs.insert(0, Text.assemble((f"{dt} ", "dim"), (status, color), (f" {layer:7} | {msg}", "green")))
            conn.close()
        except: pass
        
        # Keep only last 10 logs for display
        self.logs = self.logs[:10]

# --- Render Components ---
class BrutalDashboard:
    def __init__(self, state: BrutalState):
        self.state = state

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        # Header
        yield Align.center(Text(BANNER, style="bold green"))
        
        # Swarm Heartbeat (2-Column)
        heartbeat_table = Table(box=box.SIMPLE, expand=True, show_header=False, border_style="green")
        heartbeat_table.add_column("Executive", ratio=1)
        heartbeat_table.add_column("Swarm", ratio=1)
        
        # Executive Panel
        exec_text = Text()
        exec_text.append("■ EXECUTIVE_NODE_STATS\n", style="bold green")
        exec_text.append(f"  VERSION: {self.state.exec_vitals['version']}\n", style="green")
        exec_text.append(f"  UPTIME:  {self.state.exec_vitals['uptime']}\n", style="green")
        exec_text.append(f"  CREDITS: {self.state.exec_vitals['credits']} CR\n", style="green")
        exec_text.append(f"  STATUS:  NOMINAL", style="bold green")
        
        # Swarm Panel
        swarm_text = Text()
        swarm_text.append("■ ACTIVE_SWARM_GRID\n", style="bold green")
        for node in self.state.nodes:
            name = node.get("node_id", "UNK")
            load = node.get("load_limit", 0.0)
            ip = node.get("ip", "?.?.?.?")
            swarm_text.append(f"  {name:15} | {ip:15} | LOAD: {load*100:3.0f}%\n", style="green")
        
        heartbeat_table.add_row(exec_text, swarm_text)
        yield Panel(heartbeat_table, border_style="green", title="[ SWARM_HEARTBEAT ]", title_align="left")
        
        # Event Ticker
        ticker_panel = Text("\n").join(self.state.logs)
        yield Panel(ticker_panel, border_style="green", title="[ RECENT_EVENTS ]", title_align="left", height=12)

# --- Main Loop ---
async def main():
    console = Console()
    state = BrutalState()
    dashboard = BrutalDashboard(state)
    
    with Live(dashboard, console=console, screen=True, refresh_per_second=2) as live:
        while True:
            state.update_vitals()
            state.fetch_events()
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] SYSTEM_SHUTDOWN: Brutal exit.")
