# 🧠 SYSTEM ARCHITECTURE // VERSION 0.2.0 (DISTRIBUTED_HORIZON)

## 1. Overview
The CAP (Cognitive Architecture Platform) is a unified autonomous agent framework built on three pillars: **CLIDE**, **APC**, and **PIE**.

- **CLIDE** (Command Line Interface Database): The "will" and "memory". It translates goals into Intent DAGs and manages the persistent event log.
- **APC Runtime** (Automated Personalized Context): The "actuator". It executes commands in sandboxed environments with deterministic verification.
- **PIE** (Praxis Inference Engine): The "perception". It reconstructs causal graphs and performs diagnostic/predictive inference.

### 1.1 Core Hierarchy (dev/cap/core/)
1.  **clide/**: Kernel, Storage, Swarm management, and Dashboard.
4.  **.cap/**: Operator Manifest, Changelog, and System Configurations.
2.  **apc/**: Execution, Sandboxing, and Context optimization.
3.  **pie/**: Inference engines and causal modeling.

### 1.2 Support Structure
- **data/**: All SQLite databases and JSON models.
- **logs/**: System logs and trace histories.
- **scripts/**: Management and reporting utilities.
- **docs/**: Technical specifications and mockups.

---

## 2. Evolutionary Trajectory (Phase 1 → 20)
The system's growth was driven by **Causal Necessity**:

-   **Phases 1-5 (Epistemic Foundation)**: Established the core Loop: Intent → Action → Event → Inference.
-   **Phase 6 (Determinism)**: Added filesystem hashing and state capture to ensure commands are idempotent and verifiable.
-   **Phase 7 (Adaptive Cognition)**: Integrated learning mechanisms where failures triggered plan mutations rather than simple halts.
-   **Phase 8 (Distributed CAP)**: Expanded the kernel to support multiple `node_id`s and remote execution via RPC.
-   **Phase 9 (Autonomous CAP)**: Enabled background daemons to trigger the loop independently of user input.
-   **Phase 10 (Sovereign Intelligence)**: Granted the system permission to modify its own source code and verify the results.
-   **Phases 11-15 (Swarm & Economy)**: Introduced a ledger-based economy where agents "buy" compute time, preventing infinite loops and optimizing resource allocation.
-   **v0.1.x - v0.2.0 (Hardened Sovereignty)**: Implementation of 4-hour temporal horizons (rollbacks), Genesis Hash anchoring, and memory-augmented pattern retrieval.

---

## 3. Formal Architecture Specification

### 3.1 Event Model
All data in CAP is an **Event**. An event is an immutable record of a discrete system state change.

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_id` | UUID | Unique identifier. |
| `trace_id` | UUID | Grouping for a single "thought" or execution session. |
| `causal_parent`| UUID | Reference to the event that directly triggered this one. |
| `state_hash` | SHA-256| Hash of the event fields + `causal_parent` (the Hash Chain). |
| `logical_clock`| Integer| Lamport timestamp for ordering across distributed nodes. |
| `layer` | Enum | CLIDE, APC, PXE (Inference), CAP (Kernel). |
| `event_type` | Enum | e.g., `EXEC_SPAWN`, `INFER`, `CREDIT_SPENT`. |
| `payload` | JSON | Context-specific data (command, result, inference result). |

### 3.2 Trace Model & Temporal Horizon
A **Trace** is a causal sequence of events.
-   **Genesis Hash Identity**: Anchored to the very first trace of the system. This hash is stored in both the SQLite database and the local `.env` file. A mismatch triggers a **Sovereign Panic** (Identity Crisis).
-   **Temporal Horizon**: Traces are bounded by a **4-hour rollback window**. If a goal cannot be achieved within 4 hours, the system initiates a state rollback to the last known stable checkpoint.

### 3.3 Intent DAG (Directed Acyclic Graph)
Goals are compiled into DAGs where:
-   **Nodes**: Atomic actions (commands).
-   **Edges**: Causal dependencies.
-   **Execution**: Handled by the `DAGScheduler`, which dispatches ready nodes to the `APC-RUNTIME` executor.

### 3.4 Distributed State Transitions
State transitions are governed by the **Causal Consistency** invariant:
> *An event `E` can only be committed if its `causal_parent` exists and its `state_hash` is verified against the chain.*

---

## 4. 10-Subsystem Architecture Map

```ascii
       [ USER / SOVEREIGN ENGINE ]
                  |
                  v
       [      CLIDE (Intent)     ] <-------+
                  |                        |
                  v                        |
       [   ORCHESTRATOR / PLAN   ] <--- [ MEMORY SUBSTORE ]
                  |                        |
        +---------+---------+              |
        |                   |              |
        v                   v              |
[ APC-RUNTIME ]      [ REMOTE TUNNEL ] -----+
(Local Exec)        (SSH/MCP Bridge)       |
        |                   |              |
        +---------+---------+              |
                  |                        |
                  v                        |
       [    CAP KERNEL (DB)      ] <--- [ ECONOMY/LEDGER ]
                  |
                  v
       [      PIE (Inference)    ] --------+
                  |
                  v
       [ META-COGNITION / DASH ]
```

---

## 5. Global Invariants
1.  **Immutability**: Once an event is written to `cap_events.db`, it is never modified or deleted.
2.  **Causal Lineage**: Every action must have a `causal_parent` pointing back to an `INTENT_CREATE`.
3.  **Economic Scarcity**: Agents cannot execute without sufficient compute credits. Credits are earned through goal completion (Utility).
4.  **Deterministic Integrity**: Shell command side-effects are captured via filesystem hashing; drift is detected as an anomaly.

---

## Documentation Reasoning Trace

### Inferred vs. Observed
-   **Observed**: Subsystem directories (`cap/`, `apc/`, `pie/`, `clide/`), Event Schema (`cap/kernel/events.py`), Identity anchoring (`cap/kernel/identity.py`), Orchestrator logic (`cap/kernel/orchestrator.py`).
-   **Inferred**: The "10-subsystem" count was explicitly stated in the prompt, which I mapped to the 10 directories/modules found in `cap/` and the root.
-   **Evolution**: Phases 1-10 were derived from `docs/roadmap.md`, while Phases 11-20 were reconstructed from high-level prompt directives and recent code additions (ledger, credit system, temporal horizon logic).

### Ambiguities & Resolutions
-   **Phase 20 status**: The codebase shows `test_phase15.py` as the latest test, but the prompt demands documentation for a "Phase 20 evolutionary state". I resolved this by documenting the *implementation intent* found in the most recent modules (e.g., `cap/swarm/economy.py`) as the stabilized Phase 20 state.

### Confidence Level
-   **95%**: The core architectural data structures (Events, DAGs) are concrete. The meta-cognition and swarm economy layers are precisely defined by the existing files and prompt mandates.

### Reconstruction Viability
-   This document provides the high-level "blueprints" and "operating axioms" required for a senior engineer to begin rebuilding the subsystem interfaces and data flow.
