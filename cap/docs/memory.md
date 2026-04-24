# 🧠 MEMORY SUBSTORE & HISTORICAL RECALL

## 1. Overview
The **Memory Substore** is the system's long-term "experiential" layer. It provides a persistent repository of past execution sequences, outcomes, and environmental contexts, allowing CAP to move beyond static ontologies toward **Adaptive Cognition**.

By reinforcing successful patterns and penalizing failures, the memory system enables the system to "remember" what works in specific environments (e.g., Termux vs. Remote Linux).

---

## 2. Core Components

### 2.1 Persistence Layer (`store.py`)
Memory is stored in a dedicated SQLite database: `cap_memory.db`.
-   **Command Sequences**: Stores the full list of commands executed for a specific intent, along with their outcome (`success` or `failure`) and a `weight`.
-   **Pattern Weights**: Maintains a global ledger of `n-gram` and `dag_fragment` hashes, allowing for granular reinforcement of specific command combinations.
-   **Trace Anchoring**: Every memory entry is linked back to a `trace_id` for full causal auditability.

### 2.2 Pattern Retrieval (`retrieval.py`)
The `PatternRetriever` is the interface used by CLIDE and PIE to access historical knowledge.
-   **Successful Sequences**: Retrieves top-weighted command sequences for a given `intent_label` (e.g., `setup_workspace`).
-   **Relevant Failures**: Identifies sequences that have historically failed for an intent, providing a "negative constraint" for the compiler.
-   **Strategy Ranking**: Ranks candidate strategies by their historical success weight and temporal relevance (recency).

---

## 3. Cognitive Reinforcement Loop

Memory is updated at the end of every successful or failed trace:

1.  **Ingestion**: The `CapOrchestrator` captures the final outcome of a trace.
2.  **Storage**: The `MemoryStore` records the exact command sequence and metadata (e.g., total cycles, goal string).
3.  **Weight Adjustment**:
    -   **Success**: The weight of every command in the sequence (hashed via SHA-256) is increased by **+0.1**.
    -   **Failure**: The weight is decreased by **-0.1**.
4.  **Evolutionary Pruning**: Stale or low-weight patterns (weight < 0.1) are periodically deleted to prevent memory saturation and "interference" from outdated strategies.

---

## 4. Adaptive Compilation (Memory-Augmented CLIDE)
During intent compilation, CLIDE performs a **Memory Lookup**:
-   **Hit**: If high-weight successful sequences exist for the primitive, CLIDE **overrides** the static ontology and compiles the DAG using the literal commands found in memory.
-   **Miss**: If no high-weight memory is found, CLIDE falls back to the static `SemanticPrimitives`.

This mechanism allows the system to autonomously "discover" better ways to achieve goals (e.g., finding a more efficient set of flags for `find` or `grep`) and persist those discoveries across traces.

---

## 5. Failure Modes
| Failure | Symptom | Mitigation |
| :--- | :--- | :--- |
| **Memory Saturation** | Slow retrieval | Periodic pruning of low-weight patterns. |
| **Over-Fitting** | System repeats a "lucky" but fragile sequence | Weight decay and PIE anomaly detection. |
| **Substrate Mismatch** | Successful Termux memory fails on Remote Linux | Include environment metadata in `command_sequences`. |

---

## Documentation Reasoning Trace
-   **Observed**: SQLite schema in `store.py`, `update_pattern_weight` logic, `get_successful_sequences` ordering.
-   **Observed**: Use of `hashlib.sha256` for pattern hashes in the orchestrator.
-   **Observed**: Integration with CLIDE via `PatternRetriever` hits in `compiler.py`.
-   **Confidence Level**: 100%.
