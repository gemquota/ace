# 🧿 CAP.OS // V3.2.0 "SINGULARITY_PULSE" SPECIFICATION

This document defines the final implementation requirements for the Biome-Holographic terminal interface.

---

## 1. VISUAL TOPOGRAPHY (THE "VOID" CANVAS)
- **Margins (Bio-Rhythm):** The left and right 4-character columns are dedicated to vertical heatmaps of shifting Braille patterns (`⡷⣧⢾`). 
    - *Left Margin:* Reflects Executive Node (Termux) load.
    - *Right Margin:* Reflects aggregate Execution Node (Swarm Grid) load.
- **Center (The Constellation):** A borderless field where nodes (Agents) are positioned radially around a central ASCII "Kernel Pulse" icon.
- **Top-Down (The Waterfall):** Logs do not scroll the whole screen; they "rain" from the top in a central column, utilizing ANSI fading to disappear as they reach the orbit of the Constellation.

---

## 2. DYNAMIC BEHAVIORS
- **Orbiting Agents:** Agent symbols (`⎔`, `◈`) move in subtle elliptical paths. The speed of orbit is determined by the `success_rate` metric in `cap_arch_model.json`.
- **Holographic Threads:** When a task is dispatched, a multi-colored thread (`~·-·>`) connects the "raining" log entry to the specific orbiting agent node.
- **Temporal Fading (Z-Axis):** 
    - *Bright White/Cyan:* Brand new events and active nodes.
    - *Vibrant Green:* Maturing execution.
    - *Dim Gray:* Historical data drifting into the background.
- **Anomalous Vibration:** If an `ANOMALY_DETECTED` event occurs, the affected node and its causal threads "vibrate" (rapidly toggle between Bold Red and standard Red) to grab attention.

---

## 3. TECHNICAL STACK
- **Engine:** Python `rich.live` for high-frequency frame updates.
- **Logic:** `asyncio` loop to handle concurrent WebSocket telemetry and physics calculations.
- **Formatting:** `rich.console.Group` and `rich.layout` used internally, but borders are set to `box.MINIMAL` or hidden entirely.

---

## 4. INTERACTION MAPPING
- `[TAB]`: Toggle "Depth Focus".
    - Mode 1: Focus on Logs (Full brightness for Waterfall).
    - Mode 2: Focus on Swarm (Full brightness for Constellation).
- `[SPACE]`: Pause/Resume physics orbit.
- `[CTRL+C]`: Graceful system shutdown via `clide.kernel.syscalls.cap_trace_end`.

---
**STATUS: SPEC_LOCKED**
**TARGET: V3.2.0**
