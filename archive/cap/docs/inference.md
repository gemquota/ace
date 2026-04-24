# 🧠 Inference & Understanding (PIE Deep Dive)

## 1. Introduction
The Praxis Inference Engine (PIE) operates on the principle that "meaning is derived from sequence and effect." It takes the raw, literal truth of the execution trace (from APC-CANNON) and attempts to reconstruct the higher-order *intent* and flag any systemic *anomalies*.

## 2. Graph Construction Methodology (`pie/graph.py`)

PIE transforms the flat list of chronological events into three interconnected `NetworkX` graphs. This allows for complex structural queries (e.g., "Find all commands that affected this specific directory state").

1.  **Temporal Graph (`g_event`):**
    *   **Type:** Directed Graph (`DiGraph`)
    *   **Nodes:** Every `Event` in the trace.
    *   **Edges:** Sequentially links $E_i \rightarrow E_{i+1}$. Represents the strict arrow of time.
2.  **Causal Graph (`g_causal`):**
    *   **Type:** Directed Graph (`DiGraph`)
    *   **Nodes:** Every `Event` in the trace.
    *   **Edges:** Links $Event.causal\_parent \rightarrow Event.event\_id$.
    *   **Purpose:** Traces the explicit chain of responsibility. If an intent spawns parallel executions, this graph branches accordingly.
3.  **Entity Graph (`g_entity`):**
    *   **Type:** Undirected Graph (`Graph`)
    *   **Nodes:**
        *   Events (`type="event"`)
        *   Commands (`type="command"`, value=command string)
        *   State Changes (`type="state_change"`, value=side_effect_hash)
    *   **Edges:** Represents relationships (e.g., `EXEC_SPAWN` `belongs_to` a `command`; `EXEC_COMPLETE` `affects` a `state_change`).

## 3. Inference Algorithms (`pie/inference.py`)

The `PieInference` class analyzes the trace to produce an `InferenceState`.

### 3.1. Intent Reconstruction Logic (`_infer_intent`)
Currently, PIE uses a deterministic, heuristic approach to deduce what the user was trying to accomplish.
1.  It concatenates the `command` strings from all `EXEC_SPAWN` events in the trace.
2.  It scans this aggregate string against a predefined heuristic mapping:
    *   `mkdir` $\rightarrow$ "directory setup"
    *   `touch` $\rightarrow$ "file initialization"
    *   `pip` $\rightarrow$ "dependency management"
    *   `git` $\rightarrow$ "version control"
3.  It assigns a confidence score (currently static at `0.8`) and returns a sorted list of `intent_hypotheses`.

**Limitations:** This approach is fundamentally limited by the completeness of the mapping dictionary. It cannot infer novel combinations or semantic synonyms (e.g., `mkdir` vs `install -d`). In a production environment, this must be replaced by vector embeddings or an LLM call.

### 3.2. Anomaly Detection Strategies (`_detect_anomalies`)
PIE scans for structural and operational deviations that suggest the system is struggling to fulfill the intent.
1.  **Repeated Failure Clusters:** It calculates the total number of non-zero exit codes among `EXEC_COMPLETE` events. If failures $> 2$, it flags `REPEATED_FAILURE_CLUSTER`. This acts as a signal for the Orchestrator (or a human) to intervene, as the current DAG is likely fundamentally flawed.
2.  **Explicit Anomalies:** It scans for any events explicitly typed as `EventType.ANOMALY` (which might be emitted by the Kernel during validation or by custom extensions).

## 4. Failure Cases

*   **Silent Failures:** If a command silently fails (e.g., it prints "Error: Config missing" but exits with code `0`), PIE will completely miss the anomaly. The current logic relies strictly on `exit_code`.
*   **Hash Collisions (Theoretical):** If `hash_directory_state` produces a collision (highly unlikely with SHA-256), PIE might erroneously conclude that a side-effect occurred (or didn't occur).
*   **Trace Truncation:** If a trace is interrupted before `TRACE_END` is written, PIE will process an incomplete graph. It currently does not attempt to "heal" or auto-close open traces during ingestion.
