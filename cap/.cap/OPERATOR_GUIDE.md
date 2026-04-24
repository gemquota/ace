# 📖 CAP.OS // OPERATOR_GUIDE (V3.0.0)

This guide is the authoritative operational manual for the **Cognitive Architecture Platform**. It defines the system topology, execution workflows, and diagnostic protocols required for autonomous interaction.

---

## 🏛️ 1. SYSTEM TOPOLOGY (ARCHITECTURAL MAP)

The system operates on a tri-pillar core (`core/`) supported by a persistence layer (`data/`).

### Core Pillars:
- **CLIDE** (`core/clide/`): **Executive Branch.** 
    - *Role:* Syscalls, Event Bus, Task Scheduling, Swarm Economy, and Synaptic IDE.
    - *Key Entry:* `core/clide/kernel/orchestrator.py`
- **APC RUNTIME** (`core/apc/`): **Execution Branch.** 
    - *Role:* Sandboxed command execution with pre/post-execution filesystem hashing.
    - *Key Entry:* `core/apc/executor.py`
- **PIE** (`core/pie/`): **Analytical Branch.** 
    - *Role:* Causal graph reconstruction and diagnostic/predictive inference.
    - *Key Entry:* `core/pie/inference.py`

### Persistence Layer (`data/`):
- `cap_events.db`: The immutable master ledger of every system event.
- `cap_swarm.db`: Swarm wallets, intent marketplace, and message bus.
- `cap_arch_model.json`: System internal self-model and meta-metrics.

---

## ⚙️ 2. CAPABILITY MATRIX

| CAPABILITY | PATHWAY | INPUT | OUTPUT / SIDE EFFECT |
| :--- | :--- | :--- | :--- |
| **Inject Goal** | `clide.kernel.orchestrator` | String (Goal) | Generates `trace_id` and Intent DAG. |
| **Execute Task** | `apc.executor` | Cmd String | Sandboxed EXEC + Filesystem Hash. |
| **Diagnose** | `pie.inference` | `trace_id` | Probable Causes + Suggested Fixes. |
| **Market List** | `POST /api/intents` | Intent JSON | Added to Swarm Intent Marketplace. |
| **Visual Monitor**| `dashboard/server.py` | WebSocket | Real-time Canvas update (Port 8080). |

---

## 🚀 3. EXECUTION WORKFLOWS (PLAYBOOKS)

### Workflow Alpha: Goal-to-Trace
1. Initialize trace via `syscalls.cap_trace_start()`.
2. Inject goal into `CapOrchestrator`.
3. Monitor real-time execution nodes on the **Synaptic Canvas**.
4. Verify success via `EXEC_COMPLETE` (exit_code: 0) in `cap_events.db`.

### Workflow Beta: Deterministic Tasking
1. Populate `task_queue` in CLIDE storage.
2. Trigger `scripts/arm_worker.py` to process pending tasks.
3. Compare `pre_state_hash` vs `post_state_hash` to validate integrity.

---

## 🩺 4. DIAGNOSTIC PROTOCOLS

When system vitals (Kernel Pulse) drop:
1. **Locate:** Identify failing `trace_id` from the dashboard "Cognitive Feed".
2. **Reconstruct:** Call `pie.engine.load_trace(trace_id)` to build the causal graph.
3. **Analyze:** Run `PieInference.analyze(["diagnostic"])`.
4. **Remediate:** Execute the `suggested_fixes` and verify via a new trace.
5. **Rollback:** If integrity is compromised, use `clide.kernel.replay.cap_rollback`.

---

## 🧠 5. THE AUTOPOIETIC LOOP (SELF-EVOLUTION)

When system goals are cleared, the operator enters **Evolution Mode**:
1. **Trace Audit:** Analyze the last 100 traces for latency or failure clusters.
2. **PIE Proposal:** Use PIE to suggest structural optimizations or ontology updates.
3. **Sovereign Refactor:** Automate code updates via sandboxed verify-and-commit cycles.

---
*Status: OPERATIONAL | Modality: SOVEREIGN_HORIZON*
