# 🧠 CLIDE Compiler Mechanics (Layer 4)

## 1. Introduction
The CLIDE Compiler (`dev/cap/core/clide/compiler.py`) is the engine that converts abstract, human-readable goals into a deterministic schedule of execution. It relies on a formal ontology to map intent to concrete shell actions, bridging the semantic gap between "what I want" and "how the computer does it."

## 2. Ontology Design (`clide/ontology.py`)

The compiler uses a static `SemanticPrimitives.ONTOLOGY` to resolve goals.

### The Structure
The ontology is a dictionary where the key represents a normalized intent (e.g., `setup_workspace`), and the value is a list of action templates.

```python
ONTOLOGY = {
    "setup_workspace": [
        {"cmd": "mkdir -p {name}", "importance": 10.0},
        {"cmd": "cd {name}", "importance": 8.0},
        {"cmd": "git init", "importance": 5.0}
    ]
}
```

### 2.1 Action Primitives
*   **`cmd`:** The exact string to be executed by APC-CANNON. It supports simple Python string formatting (e.g., `{name}`) to interpolate parameters extracted from the user's goal.
*   **`importance`:** A float representing the criticality of this step. (Currently unused in Phase 5 orchestration, but designed for Phase 7 Adaptive Cognition, where the system might skip low-importance steps if the environment is constrained).

## 3. Goal $\rightarrow$ DAG Transformation Process

The `IntentCompiler.compile(goal: str, causal_parent: Optional[str] = None)` method performs the transformation:

### Step 1: Goal Parsing & Ontology Resolution
The compiler applies rudimentary keyword matching to identify the correct primitive.
*   If `"setup"` is in the goal $\rightarrow$ `setup_workspace`.
*   If `"test"` is in the goal $\rightarrow$ `test_project`.
*   If `"clean"` is in the goal $\rightarrow$ `clean_cache`.
*   Otherwise $\rightarrow$ `default` (which treats the goal as a literal shell command).

It also attempts to extract basic parameters (e.g., extracting the project name from `setup_workspace my_project`).

### Step 2: Node Generation
For the selected primitive, the compiler iterates through the action templates.
For each template, it creates an `ActionNode`:
*   `action_id`: A unique UUID4.
*   `command`: The formatted `cmd` string.
*   `dependencies`: A list containing the `action_id` of the *previously* generated node (enforcing strict sequential execution).

### Step 3: DAG Construction
The compiler bundles the generated `ActionNode` objects into an `IntentDAG`:
*   `intent_id`: A unique UUID4 for this specific compilation.
*   `goal`: The original user input.
*   `actions`: The list of `ActionNode` objects.
*   `context_refs`: A list containing the current `trace_id`.
*   `metadata`: Information about the primitive used.

### Step 4: Event Emission
The compiler serializes the `IntentDAG` and emits an `INTENT_CREATE` event to the CAP Kernel. Crucially, it attaches the `causal_parent` (passed from the Orchestrator) to anchor this new intent within the historical trace.

## 4. Scheduling & Dependency Resolution

While the `ActionNode` schema supports complex dependencies (e.g., Node C depends on Node A and Node B), the current compiler logic in `compile` generates a strictly linear chain.

```python
node = ActionNode(
    action_id=action_id,
    command=cmd,
    dependencies=[last_id] if last_id else [], # Linear dependency
    importance=t["importance"]
)
```

The Phase 5 Orchestrator (`execute_goal`) simply iterates over the `dag.actions` list in order. A true DAG scheduler (capable of parallelizing independent nodes) is slated for Phase 8 (Distributed CAP).

## 5. Limitations & Failure Modes

*   **Rigid Parsing:** The current string-matching logic is highly brittle. `setup a new workspace` works, but `create project` falls back to the default literal execution.
*   **Context Blindness:** Although `inject_context(state: InferenceState)` exists, the `compile` method does not currently use the `anomaly_flags` or `inferred_intents` to dynamically alter the DAG generation (e.g., it will blindly generate a `git init` step even if PIE previously flagged that `git` is not installed). This is the primary technical debt to be resolved in Phase 7.
