# core_clide_dashboard_server.py

## 🧩 Metadata
- **Module:** `CLIDE`
- **Subsystem:** `Dashboard`
- **Function:** API and WebSocket backend for CAP telemetry and control.
- **Source Path:** `core/clide/dashboard/server.py`

## 📝 Description
`core_clide_dashboard_server.py` is a FastAPI application that serves as the central hub for the CAP Observability Dashboard. It facilitates real-time monitoring of cognitive events, manages agent traces, provides diagnostic tools, and offers a web-based interface for interacting with the system's filesystem and swarm economy.

## 🛠️ Technical Reality

### 1. RESTful API Interface
The server exposes a wide range of endpoints for system interaction:
-   **System & Status:** `/api/status`, `/api/init` for system health and database setup.
-   **Goal Execution:** `/api/execute`, `/api/trace_status/{trace_id}` for triggering and monitoring agent goals.
-   **Diagnostics & Causal Analysis:** `/api/diagnose`, `/api/causal/{trace_id}`, `/api/traces` for inspecting trace history and troubleshooting failures using PIE.
-   **Swarm Management:** `/api/swarm/agents`, `/api/intents`, `/api/intents/buy`, `/api/swarm/ledger` for interacting with the agent-based economy and intent marketplace.
-   **Filesystem IDE:** `/api/fs/ls`, `/api/fs/read`, `/api/fs/write`, `/api/fs/mkdir`, `/api/fs/rename`, `/api/fs/delete` for a built-in code editor experience.
-   **Observability Hooks:** `/api/observability/full_mesh`, `/api/observability/causal/{trace_id}`, `/api/observability/state/{trace_id}` for generating graph data for the frontend.
-   **Control & Governance:** `/api/control/command`, `/api/control/goal` for manual injection of goals and system-level overrides.

### 2. WebSocket Streams
Provides real-time telemetry via WebSockets:
-   **Global Feed:** `/ws/live` streams all cognitive events processed by the `StreamProcessor`.
-   **Subsystem Streams:** `/ws/subsystem/{subsystem_id}` allows for focused monitoring of specific layers (CLIDE, APC, PIE, ACE, GLYPH).

### 3. Background Services
-   **Autonomous Swarm Loop:** A continuous task that simulates agent activity by periodically selecting an agent and using the `PieReasoningEngine` to decide on actions (BUY, LIST, etc.) in the swarm marketplace.
-   **Stream Processing:** Integrates with `ObservabilityAggregator` and `StreamProcessor` to aggregate and route events from the system's event bus.

### 4. Diagnostic Tools
Includes helper endpoints for UI stress testing (`/api/test/burst`) and data cleanup (`/api/test/prune`), allowing for the generation and removal of synthetic trace trees.

## 🔗 Dependencies
-   **FastAPI / Uvicorn:** Web framework and ASGI server.
-   **SQLite:** Underlying data persistence for events and swarm state.
-   **PIE Engine:** Used for trace diagnostics and autonomous reasoning.
-   **CLIDE Kernel:** Orchestrator and syscalls for goal execution.
-   **Observability Stack:** Aggregator, StreamProcessor, and StateBuilder for data normalization.
