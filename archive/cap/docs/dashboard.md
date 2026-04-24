# 🖥️ OBSERVABILITY DASHBOARD: COGNITIVE TELEMETRY

## 1. Overview
The **CAP Observability Dashboard** is a real-time, Phase 20-grade platform for monitoring the cognitive health, economic status, and swarm dynamics of the system. It utilizes a **FastAPI/WebSocket** backend to stream telemetry directly from the event log to a high-signal mono-space frontend.

---

## 2. Backend Architecture (`server.py`)

### 2.1 WebSocket Telemetry Stream (`/ws/live`)
-   **Protocol**: Pushes real-time `EVENT` packets to connected clients.
-   **Polling**: Queries the `cap_events.db` for new logical clock entries since the last push.
-   **Efficiency**: Provides low-latency updates on every system thought and action.

### 2.2 REST API Endpoints
-   **`/api/traces`**: Historical view of all execution sessions.
-   **`/api/trace/{id}`**: Deep-dive into the causal events of a specific trace.
-   **`/api/swarm/agents`**: Real-time snapshot of the agent population and wallet balances.
-   **`/api/swarm/ledger`**: View of the task marketplace (Bidding/Assignments).
-   **`/api/economy/ledger`**: Audit trail of every credit transaction.

---

## 3. Frontend Visualization (`index.html`)

The dashboard is divided into four critical monitoring panels:

### 3.1 🧬 Swarm Genesis
-   **Agent Registry**: Displays active agents, their unique IDs, and current credit balances.
-   **Live Stats**: Shows total swarm population and aggregate compute credits in circulation.

### 3.2 🚀 Real-Time Trace Timeline
-   **Event Feed**: A vertical stream of system events, color-coded by layer (CLIDE, APC, PIE).
-   **Causal Context**: Displays logical clocks and trace IDs to allow the operator to track the system's "train of thought."

### 3.3 💰 Economic Substrate
-   **Transaction Log**: Streams `CREDIT_SPENT` and `CREDIT_EARNED` events in real-time.
-   **Credit Visualization**: Highlights financial activity (Yellow for credits, Green for success bonuses).

### 3.4 ⚖️ Negotiation & Consensus
-   **Debate Log**: Visualizes the bidding process between agents.
-   **Decision Tracking**: Shows which agent won which task and the strategy they proposed.

---

## 4. Operation & Deployment
-   **Port**: Defaults to `8080`.
-   **Command**: `python3 cap/dashboard/server.py`.
-   **Substrate**: Can run on the local Android host or be tunnelled from a remote server.

---

## Documentation Reasoning Trace
-   **Observed**: FastAPI server implementation in `server.py`.
-   **Observed**: WebSocket logic and REST endpoints for swarm/economy data.
-   **Observed**: HTML/CSS/JS frontend in `index.html`.
-   **Confidence Level**: 100%.
