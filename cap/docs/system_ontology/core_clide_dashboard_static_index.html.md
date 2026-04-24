# core_clide_dashboard_static_index.html

## 🧩 Metadata
- **Module:** `CLIDE`
- **Subsystem:** `Dashboard`
- **Function:** Frontend for the Singularity Pulse Canvas and CAP.OS desktop.
- **Source Path:** `core/clide/dashboard/static/index.html`

## 📝 Description
`core_clide_dashboard_static_index.html` is a sophisticated Single-Page Application (SPA) that provides the "Singularity Pulse Canvas," the primary visual interface for the CAP system. It combines a dynamic graph visualization of the system's cognitive state with a terminal-like "desktop" for manual interaction, goal injection, and filesystem management.

## 🛠️ Technical Reality

### 1. Synaptic Canvas (Interactive Graph)
The core feature of the dashboard is an interactive graph visualization built with HTML5 Canvas:
-   **Dynamic Mesh:** Visualizes the system as a collection of nodes representing subsystems (CLIDE, APC, PIE), agents, traces, and events.
-   **Force-Directed Layout:** Employs a custom physics engine (SynapticEngine) with spring-based forces for link tension, repulsion for collision avoidance, and jitter/pulse effects to visualize cognitive load and activity.
-   **Visual Encoding:** Uses color coding and icons to distinguish node types (e.g., green for CLIDE, blue for APC, magenta for PIE, yellow for agents, red for traces).
-   **Real-Time Sync:** Integrates with the backend WebSocket (`/ws/live`) to dynamically add nodes and links as events occur in the system.
-   **Link Types:** Distinguishes between causal (red), management (yellow), and orchestration (green) relationships.

### 2. Window Manager (WM)
The interface includes a multi-window desktop environment:
-   **Tiling & Floating:** Supports both automated tiling (2x3 grid) and free-floating window management for multitasking.
-   **File Editor:** Provides a text area for viewing and editing project files, integrated with the `/api/fs/` REST endpoints.
-   **Subsystem Uplinks:** Specialized "App" windows for CLIDE, APC, and PIE that offer layer-specific graph views (e.g., CLIDE's scheduler queue, APC's thread execution, PIE's inference chain).
-   **Node Inspection:** Clicking on a graph node opens an inspector window showing its detailed JSON state.

### 3. Tactical Command & Swarm Comms
-   **Goal Injection:** A "Tactical Command" pane for manually injecting goals into specific agents or the system orchestrator (CLIDE).
-   **Swarm Chat:** A simulated "chat" interface that displays system messages and agent activity, providing a human-readable stream of cognitive intent.

### 4. HUD & Telemetry
A high-level HUD (Heads-Up Display) shows critical system metrics:
-   **Stability / Integrity / Confidence:** Displays real-time health percentages for CLIDE, APC, and PIE.
-   **Swarm Population:** Shows the number of active agents.
-   **Credit Reserve:** Tracks the total balance across the swarm's agent wallets.

## 🔗 Dependencies
-   **FastAPI Backend:** Provides the REST and WebSocket APIs used for synchronization.
-   **HTML5 Canvas:** For high-performance graph rendering.
-   **Marked.js / Prism.js:** For rendering Markdown documentation and syntax highlighting in the built-in editor.
-   **WebSockets:** For real-time event streaming.
