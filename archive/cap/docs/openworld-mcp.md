# 🌐 OPEN-WORLD SUBSTRATE & REMOTE EXECUTION

## 1. Overview
The **Open-World Substrate** is the system's interface to external environments beyond the local Termux/Android host. It enables CAP to bridge into Remote Linux/Windows servers, spawn on-demand API servers via the **Model Context Protocol (MCP)**, and interact with graphical user interfaces through **X11 Bridge Generation**.

---

## 2. Remote Execution & Tunneling (`remote_tunnel.py`)

CAP supports seamless substrate migration using the **Paramiko SSH Tunnel**.

### 2.1 The Remote Cache
To ensure resilience during network drops, the tunnel implements a **Local SQLite WAL Cache**:
-   **Persistence**: Remote events are cached in `cap_remote_cache.db`.
-   **Asynchronous Flushing**: A background thread continuously attempts to sync cached events back to the master Android database once connectivity is restored.

### 2.2 Execution Flow
-   **Migration Trigger**: If the local hardware poll detects high CPU (> 80%) or the intent is marked as "high-load," `execute_remote()` is invoked.
-   **Remote Node Identity**: Configured via `CAP_REMOTE_IP` and `CAP_REMOTE_USER`.
-   **Command Dispatch**: Commands are executed via SSH; `stdout`, `stderr`, and `exit_code` are captured and returned to the master orchestrator.

---

## 3. On-Demand MCP Servers (`mcp_generator.py`)

CAP can spawn **FastAPI-based JSON-RPC servers** to expose its internal state or allow remote agents to inject intents.

### 3.1 Security & Inactivity Guard
-   **Kill-Switch**: MCP servers monitor activity. If no requests are received for **5 minutes (300 seconds)**, the server autonomously triggers a `SIGINT` and shuts down to conserve resources.
-   **Read-Only Endpoints**: Exposes `/events` and `/traces/{trace_id}` for remote observability.
-   **JSON-RPC Dispatcher**: A `/rpc` endpoint handles standardized MCP methods (e.g., `execute_intent`, `get_status`).

---

## 4. X11 GUI Bridging (`x11_bridge.py`)

For interacting with visual environments, CAP generates and executes **GUI Interaction Scripts**.

### 4.1 Script Generation
-   **Tkinter Bridge**: Generates stylized, atomic UI scripts for rapid prototyping or state capture.
-   **PyQt Bridge**: Generates more complex, multi-widget UI scripts for professional-grade interaction.

### 4.2 Automated State Capture
-   **Dynamic UI**: The system generates scripts based on a `ui_layout` string.
-   **Autoclick / Headless Support**: Scripts include an autonomous `root.after()` or `QTimer` trigger to perform actions and destroy the window, allowing for automated UI testing.
-   **JSON Telemetry**: X11 scripts print their final state as JSON to `stdout`.
-   **X11 Hashing**: PIE captures this JSON output to generate a `post_state_hash` of the GUI interaction, treating the UI as a measurable side-effect.

---

## 5. Failure Modes
| Failure | Symptom | Mitigation |
| :--- | :--- | :--- |
| **SSH Drop** | Remote sync error | `RemoteCache` WAL persistence and async flushing. |
| **Display Missing** | X11 script failure | Fallback to headless mode or `xvfb`. |
| **Zombie MCP** | Resource leak | 5-minute inactivity kill-switch. |

---

## Documentation Reasoning Trace
-   **Observed**: 5-minute kill-switch in `mcp_generator.py`.
-   **Observed**: Remote cache sync thread in `remote_tunnel.py`.
-   **Observed**: Tkinter/PyQt generation and JSON state capture in `x11_bridge.py`.
-   **Confidence Level**: 100%.
