# 📟 CAP.OS // V3.1.0 TERMINAL STARTUP VARIANTS

These variants define the CLI "Splash & Status" screen that appears when you run `python scripts/startup_dashboard.py` or initialize the mesh.

---

## 💀 1. THE BRUTAL_ANSI (Matrix/Forensic)
**Visuals:** Raw, monochromatic (Green on Black). Uses `[ OK ]` or `[ FAIL ]` style boot logs.
- **Layout:** 
    - Top: A massive ASCII-art "CAP OS" banner. 
    - Middle: A 2-column "Swarm Heartbeat" list.
    - Bottom: A scrolling ticker of the last 5 events from `cap_events.db`.
- **Interactivity:** Non-blocking. The screen refreshes every 2 seconds using `clear` or ANSI escape codes to maintain a "live" feel without flooding scrollback.
- **Emoji:** 🟢 🔴 📡 💀

---

## 🗄️ 2. THE GRID_TUI (Box-Drawing/Tabular)
**Visuals:** Uses Unicode Box-Drawing characters (┌─┐) to create distinct "Panels" in the terminal.
- **Layout:**
    - Panel 1 (Top Left): System Vitals (Uptime, CR Balance, Version).
    - Panel 2 (Top Right): Active Node Registry (IPs and Load).
    - Panel 3 (Bottom): The Celery Task Queue visualized as a horizontal bar chart.
- **Interactivity:** Uses `rich.live` or `textual` style rendering to update specific boxes without flickering.
- **Emoji:** 🛡️ 🔫 🧠 💾 🤖

---

## ⚡ 3. THE LIGHTNING_PROMPT (Minimalist/Action-First)
**Visuals:** Extremely sparse. Focuses on a single "Status Line" at the bottom of the terminal.
- **Layout:** 
    - A single line of text that constantly updates: `CAP v3.1.0 | Swarm: 12 Active | Task: FS_SCAN (45%) | 🪙 12,450.22`
    - Above it, only the most critical `WARNING` or `ANOMALY` events appear.
- **Interactivity:** Your terminal prompt is immediately available. The UI lives in the "Header" or "Footer" of your shell.
- **Emoji:** ⚡ 🔗 📈

---

## 🎰 4. THE MARKET_LEDGER (Financial/Ticker)
**Visuals:** Heavy use of color-coded text (Red for cost, Green for profit).
- **Layout:**
    - Top: A horizontal scrolling "Intent Ticker" using Unicode arrows (▲/▼).
    - Center: A "Top Performers" leaderboard of agents.
    - Right-Sidebar: A vertical list of the most expensive intents currently in the Redis queue.
- **Interactivity:** Optimized for monitoring economic "Selection Pressure".
- **Emoji:** 💎 📈 💸 🎰

---

## 🪐 5. THE ORBITAL_STREAM (Zen/Fluid)
**Visuals:** Uses Braille patterns or special Unicode characters to create "Sparkline" graphs of activity.
- **Layout:** 
    - Instead of boxes, the data flows in a single stream.
    - Each node's activity is represented by a pulsing dot that moves across the screen.
    - Causal links are represented by indentations: a sub-task is indented under its parent goal.
- **Interactivity:** Feels like reading a "Biological Pulse" of the machine.
- **Emoji:** 🌌 🧬 🫧 🪐

---

## 🏁 SELECTION PROTOCOL
Which of these **Terminal-Native** layouts should we refine? 
- **1 (Brutal)** is for the "Hacker" aesthetic.
- **2 (Grid)** is for the "Pro-Dashboard" aesthetic.
- **3 (Lightning)** is for the "High-Speed Operator" aesthetic.
