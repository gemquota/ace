# ⚙️ EXECUTION MODEL: DETERMINISM & STATE CAPTURE

## 1. Overview
The CAP **Execution Model** defines the boundaries of deterministic interaction with the host environment. It treats every command as a **State Transformation Function** ($f(S_{pre}, C) \to S_{post}$), where side-effects are captured through cryptographic filesystem hashing.

---

## 2. Determinism Boundaries

CAP enforces determinism through three primary constraints:

### 2.1 Spatial Isolation (Sandboxing)
-   Commands are restricted to a unique `cwd` (~/.cap_sandbox).
-   Path traversal is blocked via denylists and `validate_command`.
-   Filesystem state is localized to the sandbox directory.

### 2.2 Temporal Bounding
-   **Timeouts**: Every execution is bounded by a mandatory wall-clock timeout (default 5s).
-   **Lamport Logical Clocks**: Ensures a consistent total ordering of events across multiple agents, regardless of physical arrival time.

### 2.3 Side-Effect Verifiability
Side-effects are measured as the **Delta** between `pre_state_hash` and `post_state_hash`.
-   **Drift Detection**: If a command completes successfully but the `post_state_hash` does not match the predicted state from PIE, a `DRIFT_DETECT` anomaly is raised.
-   **Idempotency**: By capturing state hashes, CAP can verify if a command needs to be re-run or if the environment is already in the target state.

---

## 3. The 4-Hour Temporal Horizon

CAP implements a **Rolling Temporal Horizon** to limit the scope of catastrophic failure.
-   **Window**: Traces are conceptually bounded by a 4-hour window from `TRACE_START`.
-   **Enforcement**: The `CapOrchestrator` checks `current_time - trace_start_time`.
-   **Rollback**: If the window is breached, the system initiates an autonomous `ROLLBACK` event, reverting the filesystem state to the last verified `CHECKPOINT`.

---

## 4. Substrate Migration (Substrate-Agile Execution)

Execution is not bound to a single physical host.
-   **Hardware Triggers**: The `AutonomousLoop` polls CPU/Thermal metrics. If CPU > 80% or thermal warning = True, the system sets `CAP_SUBSTRATE_MIGRATE=1`.
-   **Transparent Routing**: The Orchestrator intercepts the command and routes it through the `RemoteTunnel` (SSH/Paramiko) to a higher-capacity substrate.
-   **Event Continuity**: The remote `exit_code` and output are returned and committed to the master trace as if they occurred locally, preserving the causal chain.

---

## Documentation Reasoning Trace
-   **Observed**: Hashing logic in `hasher.py`, Sandbox logic in `sandbox.py`.
-   **Observed**: 4-hour check and substrate migration logic in `orchestrator.py` and `loop.py`.
-   **Observed**: Identity and clock logic in `identity.py` and `clock.py`.
-   **Confidence Level**: 100%.
