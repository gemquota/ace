# 🐚 CAP KERNEL & CORE SUBSYSTEMS

## 1. Overview
The **CAP Kernel** is the central arbiter of truth, identity, and causality within the Cognitive Architecture Platform. It is responsible for the immutable commitment of events, the maintenance of logical time, and the enforcement of the 4-hour temporal horizon. The kernel ensures that no action occurs without a verifiable lineage and that the system's identity remains anchored to its Genesis.

---

## 2. Core Components

### 2.1 Identity & Genesis Anchoring (`identity.py`)
The system's identity is defined by a **Genesis Hash**, generated during the first trace of a workspace. 
-   **Storage**: Persisted in both `cap_events.db` (`system_identity` table) and the `.env` file as `CAP_GENESIS_HASH`.
-   **Verification**: On every startup, the kernel compares the DB hash and the `.env` hash. A mismatch (e.g., from an unauthorized filesystem restore or DB tampering) results in a `RuntimeError: CRITICAL IDENTITY MISMATCH`.
-   **Function**: `init_genesis(trace_id: str)` ensures the hash is established or verified.

### 2.2 Event Model (`events.py`)
The `Event` class is the primary data structure for all system transitions.
-   **Hashing**: `_calculate_hash()` computes a SHA-256 hash of all metadata + the `causal_parent`. This creates a cryptographic hash chain for every trace.
-   **Logical Ordering**: Each event carries a `logical_clock` (Lamport timestamp) and a `timestamp` (wall-clock time).
-   **Node Attribution**: Every event is tagged with a `node_id` (default: "default_node"), allowing for distributed trace reconstruction.

### 2.3 Syscalls: The System Interface (`syscalls.py`)
The `syscalls` module provides the API for all other subsystems (CLIDE, APC, PIE) to interact with the kernel.
-   `cap_trace_start()`: Initializes a new execution trace, registers the local node, and commits a `TRACE_START` event.
-   `cap_event_commit(trace_id, layer, event_type, payload, causal_parent)`: The primary mechanism for appending to the event log. It automatically handles logical clock ticking and real-time timestamping.
-   `spawn_agent_trace(parent_trace_id, agent_id)`: Creates a branched trace for parallel multi-agent execution (Phase 20 Swarm logic).

### 2.4 Logical Clock & Temporal Ordering (`clock.py`)
The kernel implements a standard **Lamport Logical Clock**.
-   `tick()`: Increments the local clock on every event emission.
-   `update(received_time)`: Updates the local clock based on events received from remote nodes, ensuring $C(e_{recv}) > C(e_{send})$.

### 2.5 Causal Validator (`validator.py`)
Ensures the integrity of the event log during ingestion or replay.
-   **Integrity Checks**: Verifies `state_hash` matches re-calculated content.
-   **Linearity**: Ensures `logical_clock` and `timestamp` are monotonically increasing.
-   **Lineage**: Enforces that non-root events MUST have a `causal_parent`.

---

## 3. Orchestration & Scheduling

### 3.1 CapOrchestrator (`orchestrator.py`)
The high-level controller for a single trace.
-   **Strategy Modes**:
    -   `ADAPTIVE`: Switches between conservative and aggressive based on success rates.
    -   `CONSERVATIVE`: Halts immediately on any action failure.
-   **Temporal Horizon Check**: `check_temporal_horizon()` calculates the elapsed time from the trace start. If it exceeds **4 hours**, the orchestrator refuses to proceed and suggests a rollback.
-   **Compute Weighting**: Automatically routes "high-load" intents (e.g., builds, stress tests) to remote substrates via the `RemoteTunnel`.

### 3.2 DAGScheduler (`scheduler.py`)
Manages the execution of the `IntentDAG`.
-   **Parallelism**: Uses a `ThreadPoolExecutor` to dispatch independent actions.
-   **Status Tracking**: Monitors nodes through `PENDING`, `READY`, `RUNNING`, `SUCCESS`, and `FAILED`.
-   **Asynchronous Execution**: Supports both local `executor.execute_command` and remote `task_queue` dispatching.

---

## 4. Autonomous Loop (`loop.py`)
The Phase 20 background engine that enables continuous sovereign operation.
-   **Observation**: Continuously ingests events and performs PIE inference.
-   **Drift Detection**: Uses `_detect_drift()` to identify failure clusters or low success rates, triggering `healer.heal_system()`.
-   **Sovereign Goals**: Injects autonomous goals (e.g., "verify integrity") when the system is idle.
-   **Hardware Polling**: Monitors CPU usage and thermal state via `psutil`. If limits are breached (e.g., CPU > 80%), it sets `CAP_SUBSTRATE_MIGRATE=1`, triggering the orchestrator to route tasks remotely.

---

## 5. Failure Modes & Recovery
-   **SQLite Locking**: Handled via connection retries in `cap.storage.db`.
-   **Identity Crisis**: If `CAP_GENESIS_HASH` is lost, the system cannot verify lineage.
-   **Causal Break**: If an event's `causal_parent` is missing, PIE cannot construct the graph, triggering an `ANOMALY` event.

---

## Documentation Reasoning Trace

### Inferred vs. Observed
-   **Observed**: Lamport clock implementation in `clock.py`, Syscall wrappers in `syscalls.py`, DAG scheduling logic in `scheduler.py`.
-   **Inferred**: The "4-hour temporal horizon" is implemented as a check in `orchestrator.py` rather than a hard kernel-level timeout, though it is described as a "Kernel horizon".
-   **Hardware Polling**: Observed the `psutil` integration in `loop.py` and the `CAP_SUBSTRATE_MIGRATE` trigger.

### Confidence Level
-   **100%**: The kernel logic is the most mature and explicitly defined part of the codebase.

### Reconstruction Viability
-   This specification allows for a complete reconstruction of the kernel's event-handling logic, the logical clock system, and the primary orchestration loop.
