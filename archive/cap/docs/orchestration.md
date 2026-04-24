# 🎼 ORCHESTRATION & EXECUTION FLOW

## 1. Overview
**Orchestration** is the "connective tissue" that binds Intent (CLIDE), Action (APC), and Inference (PIE) into a unified cognitive cycle. It manages the lifecycle of a trace, routes tasks across the swarm, and mutates the execution plan in real-time based on environmental feedback.

---

## 2. Orchestration State (`planner.py`)

The **Orchestration State** tracks the real-time status of a plan:
-   **`active_nodes`**: Nodes currently dispatched to the executor.
-   **`completed_nodes` / `failed_nodes`**: The execution history of the current DAG.
-   **`strategy`**: The current execution mode (`AGGRESSIVE`, `CONSERVATIVE`, `ADAPTIVE`).
-   **`inferred_state`**: The most recent `InferenceState` from PIE, providing context for plan mutations.

---

## 3. Plan Mutation Engine (`planner.py`)

CAP is not a static executor; it can **fundamentally rewrite its plan** mid-execution.

### 3.1 Real-Time Mutations
-   **Action Insertion**: `insert_node()` allows the orchestrator to inject new corrective actions (e.g., installing a missing package) into the DAG before a failed node is retried.
-   **Action Skipping**: `skip_node()` marks a node as complete if its goal was achieved by a previous side-effect (detected via PIE).
-   **Strategy Switching**: `update_strategy()` allows the system to switch from `ADAPTIVE` to `CONSERVATIVE` if the success rate drops, preventing catastrophic failure cascades.

### 3.2 Suggestive Correction
Using the PIE Diagnostic Flavour, the planner suggests **Heuristic Repairs**:
-   **Missing Dependency**: If `stderr` indicates a missing executable, it suggests an `apt install` or `pip install` node.
-   **Missing Directory**: If a directory is missing, it suggests a `mkdir -p` node.

---

## 4. Multi-Agent Trace Routing (`router.py`)

In Phase 20, the Orchestrator supports **Parallel Branching**:
1.  **Agent Spawning**: The loop spawns multiple agents (e.g., "Speed Demon", "Conservative Guard") on independent branch traces.
2.  **Execution**: Each agent executes the same goal using their preferred strategy.
3.  **Winning Trace**: The `TraceRouter` evaluates the results.
4.  **Master Merge**: The trace with the **highest success rate** and **lowest credit cost** is selected and merged back into the master timeline via a `MERGE_AGENT` event.

---

## 5. Execution Loops & Cycles

The `CapOrchestrator` (`orchestrator.py`) manages the dynamic loop:
-   **Dispatch**: Ready nodes from the `DAGScheduler` are sent to the executor.
-   **Incremental Inference**: PIE is invoked after *every* command completion to update the state.
-   **Temporal Horizon Guard**: The orchestrator checks if the trace has exceeded the **4-hour temporal horizon**. If breached, it halts and triggers a `ROLLBACK` event.

---

## 6. Failure Modes
| Failure | Symptom | Mitigation |
| :--- | :--- | :--- |
| **Deadlock** | Scheduler halts | Cycle limit (`max_cycles=20`) and timeout enforcement. |
| **Mutation Loop** | Infinite corrections | Mutation depth limits and `CONSERVATIVE` strategy switch. |
| **Trace Divergence** | Merge fails | router chooses the "least-bad" trace or triggers a `GENESIS_BAILOUT`. |

---

## Documentation Reasoning Trace
-   **Observed**: Parallel branching and trace routing in `router.py`.
-   **Observed**: Action insertion and skipping logic in `planner.py`.
-   **Observed**: 20-cycle limit and 4-hour horizon check in `orchestrator.py`.
-   **Confidence Level**: 100%.
