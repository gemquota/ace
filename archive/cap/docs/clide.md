# 🧩 CLIDE: COGNITIVE LOOP INTENT DISTRIBUTION ENGINE

## 1. Overview
**CLIDE (Cognitive Loop Intent Distribution Engine)** is the "will" and "reasoning" layer of the CAP architecture. It acts as a compiler that translates high-level semantic goals—whether from a user or the Sovereign Engine—into executable, machine-readable **Intent DAGs (Directed Acyclic Graphs)**.

CLIDE's primary function is to resolve the ambiguity of natural language into a deterministic sequence of atomic actions, constrained by the system's current knowledge and the local substrate's capabilities.

---

## 2. Intent DAG Structure (`schema.py`)

An **Intent DAG** represents a structured plan of execution.

### 2.1 Action Node (`ActionNode`)
-   **`action_id`**: A unique identifier for the specific step.
-   **`command`**: The literal shell command to be executed.
-   **`dependencies`**: A list of `action_id`s that must successfully complete before this node is dispatched.
-   **`importance`**: A priority score (0.0 to 10.0) used by the `DAGScheduler` for ordering.
-   **`constraints`**: Substrate-specific execution requirements (e.g., timeout, memory limits).

### 2.2 Intent DAG (`IntentDAG`)
-   **`intent_id`**: A unique ID for the entire plan.
-   **`goal`**: The original natural language string that triggered the compilation.
-   **`actions`**: A list of `ActionNode` objects.
-   **`metadata`**: Contextual flags (e.g., the `primitive` key used for ontology mapping).
-   **`context_refs`**: References to the `trace_id` and previous `event_id`s that informed this plan.

---

## 3. The Compilation Pipeline (`compiler.py`)

CLIDE follows a three-stage pipeline to transform a goal into a DAG:

1.  **Semantic Mapping**:
    -   The compiler identifies a **Primitive Key** from the goal (e.g., `setup_workspace`, `test_project`, `clean_cache`).
    -   If no primitive matches, it falls back to a `default` primitive (direct command execution).
2.  **Memory-Augmented Overrides (Phase 16)**:
    -   The compiler queries the `PatternRetriever` for the most successful historical sequence associated with the identified primitive.
    -   If a "Memory Hit" occurs, the static ontology is bypassed in favor of the proven, successful sequence of literal commands.
3.  **Ontology Expansion**:
    -   If no memory hit occurs, the compiler expands the primitive using the **Semantic Ontology**.
    -   Placeholders in the ontology (e.g., `{name}`, `{goal}`) are formatted using parameters extracted from the goal.
4.  **DAG Generation & Commitment**:
    -   The expanded template is converted into a list of `ActionNode`s with linear dependencies.
    -   An `INTENT_CREATE` event is committed to the CAP Kernel, recording the full DAG and its causal parent.

---

## 4. Semantic Ontology (`ontology.py`)

The **Ontology** is a dictionary of semantic primitives mapped to action templates.

| Primitive | Action Templates | Purpose |
| :--- | :--- | :--- |
| `setup_workspace` | `mkdir`, `cd`, `git init` | Basic project bootstrapping. |
| `test_project` | `pytest`, `python3 -m unittest` | Validation and verification. |
| `clean_cache` | `rm -rf __pycache__`, `find -delete` | Workspace housekeeping. |
| `default` | `{goal}` | Fallback for direct command execution. |

---

## 5. Synthetic Intent Generation (`synthetic.py`)

CLIDE can autonomously synthesize intents based on the system's internal state (Phase 17 logic).

-   **Anomaly Repair**: If a `HISTORICAL_FAILURE` is detected in the `InferenceState`, CLIDE synthesizes a `repair_historical_anomaly` intent to validate environment consistency.
-   **Environment Stabilization**: If execution stability is low (< 0.6), a `stabilize_environment` intent is generated to check resource limits.
-   **Discovery**: For new traces with few commands, it generates a `map_workspace` intent (`ls -F .`).
-   **Housekeeping**: After high activity (> 20 commands), it synthesizes `optimize_storage` to clean caches.

---

## 6. Dynamic Tool Forging

When a goal explicitly requests to **"forge tool {name}"**, CLIDE enters a specialized mode:
1.  **Code Generation**: It generates a Python script that implements the requested logic (initially a boilerplate echo).
2.  **Substrate Injection**: The script is written to the `tools/` directory with a unique hash.
3.  **Ontology Mutation**: A new primitive is dynamically added to the `SemanticPrimitives.ONTOLOGY`, allowing the new tool to be called as a native command in future compilation passes.

---

## 7. Failure Modes & Limitations
-   **Ambiguous Mapping**: If multiple primitives match, CLIDE defaults to the first one found (deterministic but potentially inaccurate).
-   **Ontology Brittleness**: Static templates may fail if the environment changes (mitigated by Phase 16 Memory hits).
-   **Parameter Extraction**: Extraction of params (like `{name}`) is currently heuristic-based and may fail for complex phrasing.

---

## Documentation Reasoning Trace

### Inferred vs. Observed
-   **Observed**: DAG schema in `schema.py`, Mapping logic and tool forging in `compiler.py`, Ontology primitives in `ontology.py`, Synthetic intent triggers in `synthetic.py`.
-   **Observed**: The interaction between CLIDE and the `PatternRetriever` for historical sequence overrides.
-   **Inferred**: The "ambiguous mapping" failure mode as a direct consequence of the `if/elif` structure in the compiler's mapping logic.

### Confidence Level
-   **100%**: The source code provides a complete and unambiguous definition of the intent compilation process.

### Reconstruction Viability
-   This specification allows for a complete reconstruction of the CLIDE compiler, the intent schema, and the autonomous intent synthesis logic.
