# 🧠 PIE: PRAXIS INFERENCE ENGINE

## 1. Overview
The **Praxis Inference Engine (PIE)** is the "perception" and "learning" layer of the CAP architecture. It is responsible for ingesting immutable event traces, reconstructing the underlying causal and temporal relationships, and performing multi-flavor inference to explain past failures and predict future actions.

PIE transforms raw event data into **Inference States**, which are then consumed by CLIDE (the Intent Compiler) and the Sovereign Engine to close the cognitive loop.

---

## 2. Core Components

### 2.1 Trace Ingestion & Validation (`engine.py`)
The `PieEngine` serves as the entry point for analysis.
-   **Loading**: Retrieves all events for a specific `trace_id` from the CAP Kernel.
-   **Verification**: Performs a mandatory validation pass on every event in the trace (via `validate_event`) before analysis. Any corruption or causal break in the trace results in an immediate `ValueError`.

### 2.2 Trace Graphing (`graph.py`)
PIE utilizes **NetworkX** to build three distinct graph representations of a trace:
1.  **Event Graph (`g_event`)**: A directed graph representing the strict temporal sequence of events (Temporal Edges).
2.  **Causal Graph (`g_causal`)**: A directed acyclic graph (DAG) representing the logical lineage of events via `causal_parent` references (Causal Edges).
3.  **Entity Graph (`g_entity`)**: An undirected graph connecting events to physical entities like commands, side-effect hashes, and filesystem states.

### 2.3 Inference Logic (`inference.py`)
The `PieInference` class orchestrates the analysis of a trace using multiple specialized "flavours."
-   **Inference State**: A unified object containing `intent_hypotheses`, `anomaly_flags`, `execution_summary`, and `predictions`.
-   **Anomaly Detection**: Identifies repeated failure clusters (e.g., the same command failing > 2 times) and historical failure matches via the `PatternRetriever`.

### 2.4 Model Evolution (`PieModelEngine`)
PIE maintains a persistent state (`pie_model.json`) that evolves over time.
-   **Causal Weights**: Tracks the frequency of transitions between commands (e.g., `mkdir` → `cd`).
-   **Economic Weighting (Phase 20)**: Transition weights are boosted (1.2x) for successful sequences and penalized (0.5x) for failures, reflecting the "survival of the fittest" economic pressure.
-   **Temporal Patterns**: Correlates command pairs with their joint success rate to calculate prediction confidence.

---

## 3. Inference Flavours (`pie/flavours/`)

PIE uses a pluggable architecture for specialized analysis:

### 3.1 Diagnostic Flavour
Focuses on explaining **Execution Failures**.
-   **Failure Point Identification**: Traces `EXEC_COMPLETE` failures back to their `EXEC_SPAWN` parents.
-   **Cause Mapping**: Heuristically maps `stderr` patterns (e.g., "command not found," "no such file or directory") to probable causes and suggested fixes.

### 3.2 Predictive Flavour
Focuses on forecasting the **Next Action**.
-   **Causal Forecasting**: Uses the `PieModelEngine`'s causal weights to suggest the top 3 most likely next commands based on the current execution context.
-   **Confidence Scoring**: Predictions are ranked by their historical frequency and success correlation.

---

## 4. Key Mechanisms

### 4.1 Prediction & Deviation Detection
On every analysis cycle, PIE:
1.  Identifies the `last_command` in the current trace.
2.  Fetches predictions from the model engine.
3.  If the *actual* next action deviates significantly from high-confidence predictions, an `ANOMALY` flag is raised, signaling a potential drift in system behavior.

### 4.2 Pattern Recognition & Memory Integration
PIE integrates with the **Memory Substore** via the `PatternRetriever`:
-   It checks if the current failing intent matches any historically failing patterns.
-   If a match is found, it injects a `HISTORICAL_FAILURE_MATCH` flag into the inference state, which the Sovereign Engine uses to trigger a root-cause analysis goal.

---

## 5. Failure Modes
| Failure | Symptom | Detection |
| :--- | :--- | :--- |
| **Trace Corruption** | `ValueError` during load | Kernel `validate_event` check. |
| **Graph Inconsistency** | `nx.NetworkXError` | Missing `causal_parent` or cyclic dependencies. |
| **Prediction Drift** | Low confidence in `predictions` | Model engine weight decay. |
| **Memory Isolation** | Missing `HISTORICAL_FAILURE_MATCH` | `PatternRetriever` timeout or DB lock. |

---

## Documentation Reasoning Trace

### Inferred vs. Observed
-   **Observed**: Use of NetworkX for graph construction (`graph.py`), Persistence in `pie_model.json` (`inference.py`), Diagnostic mapping in `flavours/diagnostic.py`.
-   **Observed**: Economic weighting (1.2x/0.5x) in the `evolve` method of `PieModelEngine`.
-   **Inferred**: The interaction between PIE and CLIDE (Intent Compiler) is inferred as a feedback loop where CLIDE consumes `intent_hypotheses` to refine its next compilation pass.

### Ambiguities & Resolutions
-   **Command Base Heuristic**: I observed that PIE uses `command.split()[0]` as a "command base." I've documented this as a heuristic, as it may fail for complex shell pipelines or prefixed commands.

### Confidence Level
-   **98%**: The code is highly explicit about its data flow and inference logic.

### Reconstruction Viability
-   This specification provides the exact formulas for model evolution, the structure of the trace graphs, and the logic for the diagnostic/predictive flavours.
