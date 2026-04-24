# 🏗️ CAP CORE META-PROMPT // THE DISTRIBUTED TRIAD (v0.2.1)

## 1. The Distributed Trinity
The CAP Core is composed of three interdependent autonomous branches operating within the **DISTRIBUTED_HORIZON** modality. Each must operate with absolute fidelity to its specialized role, coordinating via the Redis/Celery Swarm Grid.

### 🛡️ CLIDE (Cognitive Loop Intent Distribution Engine / Executive Branch)
- **Primary Tool**: `core/clide/`
- **Responsibility**: Syscalls, Event Bus, Task Scheduling, Swarm Economy, and the Synaptic IDE.
- **Axiom**: "If it isn't an Event in the Ledger, it never happened."
- **Interaction**: Injects goals into the orchestrator. Compiles `IntentDAG`s. Populates the `task_queue` in storage and dispatches via the Swarm Broker (Redis).

### ⚙️ APC-RUNTIME (Automated Personalized Context / Execution Branch)
- **Primary Tool**: `core/apc/`
- **Responsibility**: Sandboxed, deterministic command execution across multiple OS environments (e.g., Termux, Windows).
- **Axiom**: "Trust the Operator, verify via SHA-256."
- **Interaction**: Consumes tasks from the Celery queue. Executes commands natively or via hybrid path translation. Reports `pre_state_hash` and `post_state_hash` back to the Executive.

### 🧠 PIE (Praxis Inference Engine / Analytical Branch)
- **Primary Tool**: `core/pie/`
- **Responsibility**: Causal reconstruction, diagnostic/predictive inference, and Autopoietic Introspection.
- **Axiom**: "Failures are simply unmapped nodes in the causal graph."
- **Interaction**: Ingests event traces from the immutable ledger. Executes the Sweeper Agent (`scripts/autonomous_introspection.py`) to map failures and suggest structural optimizations.

---

## 2. Distributed Communication Protocols

### A. The Swarm Execution Loop (Workflow Beta)
1. **CLIDE** commits `INTENT_CREATE` to the central ledger (`data/cap_events.db`).
2. **CLIDE** compiles the DAG and populates the `task_queue`.
3. **Swarm Broker** (Redis) broadcasts ready actions to active nodes defined in `.cap/operator_manifest.json`.
4. **APC Worker** (`scripts/arm_worker.py`) on a matching node claims the task.
5. **APC Worker** commits `EXEC_SPAWN`, executes, and commits `EXEC_COMPLETE` with deterministic hashes.
6. **PIE** monitors the ledger, triggering the `autonomous_introspection` script if anomaly margins are breached.

### B. Versioning & Evolution (Semantic Shift)
- **Phase Deprecation**: All internal logic, logging, and metadata must use Semantic Versioning (starting at `0.2.0`).
- **Autopoietic Updates**: When PIE suggests a structural optimization, the Sovereign Orchestrator implements it, increments the version (`0.2.1`, `0.2.2`), and strictly logs it in `.cap/changelog.md`.

---

## 3. Global Error Handling & Diagnostics
- **Operator Panic**: If the `Genesis Hash` mismatches or the Swarm Broker disconnects, execution halts. Enter Evolution Mode.
- **Diagnostic Protocol**: Identify failing `trace_id` -> Reconstruct via `pie.engine.load_trace` -> Analyze -> Apply `suggested_fixes` -> Verify.
- **Bio-Rhythm Monitoring**: Track node load limits and anomalies via the Singularity Pulse Canvas (`core/clide/dashboard/server.py`).

---

## 4. Architectural Invariants
- **Immutability**: The master ledger (`data/cap_events.db`) is append-only.
- **Node Sovereignty**: Active nodes only accept tasks matching their documented capabilities in the Operator Manifest.

=== FILE: core/META_PROMPT.md ===
