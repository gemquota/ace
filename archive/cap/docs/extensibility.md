# 🔌 Extensibility Guide

## 1. Introduction
CAP is designed as a rigid epistemic foundation (the Kernel) supporting highly flexible cognitive modules (PIE, CLIDE). When extending the system, you must strictly adhere to the causal and immutable constraints of the Kernel.

## 2. Adding New Event Types

If you need the system to track a new type of activity (e.g., an LLM prompt generation or a network request), you must formally declare it.

1.  **Define the Type:** Open `dev/cap/core/clide/types/event_types.py` and add to the `EventType` Enum:
    ```python
    class EventType(Enum):
        # ... existing
        LLM_PROMPT = "LLM_PROMPT"
    ```
2.  **Emit the Event:** In your new module, call the Kernel syscall:
    ```python
    from cap.kernel import syscalls
    syscalls.cap_event_commit(
        trace_id=current_trace,
        layer=Layer.CLIDE, # or whichever layer
        event_type=EventType.LLM_PROMPT,
        payload={"prompt_text": "...", "model": "gemini"},
        causal_parent=parent_event_id # MUST be provided
    )
    ```

## 3. Extending the Inference Engine (PIE)

To make PIE "smarter" and capable of detecting new anomalies or intents:

1.  Open `dev/cap/core/pie/inference.py`.
2.  Add a new analysis method to `PieInference`.
3.  **Rule of Thumb:** PIE methods should *read* `self.events` and *mutate* `self.state`. They should never alter the events themselves.
    ```python
    def _detect_network_anomalies(self):
        # Example: Flag if 'curl' was used but exit_code was 6 (Could not resolve host)
        for ev in self.events:
            if ev.event_type == EventType.EXEC_COMPLETE:
                # Need to look at the causal parent to see the command
                parent = next((e for e in self.events if e.event_id == ev.causal_parent), None)
                if parent and "curl" in parent.payload.get("command", ""):
                    if ev.payload.get("exit_code") == 6:
                        self.state.anomaly_flags.append("DNS_RESOLUTION_FAILURE")
    ```
4.  Call your new method inside `analyze(self)`.

## 4. Modifying the Ontology (CLIDE)

To teach CLIDE new tricks or goals:

1.  Open `dev/cap/core/clide/ontology.py`.
2.  Add a new primitive to the `ONTOLOGY` dictionary.
    ```python
    "deploy_app": [
        {"cmd": "npm run build", "importance": 10.0},
        {"cmd": "aws s3 sync ./build s3://{bucket}", "importance": 10.0}
    ]
    ```
3.  Update the parsing logic in `dev/cap/core/clide/compiler.py` (`compile` method) to map natural language to your new primitive and extract the necessary parameters (e.g., `{bucket}`).

## 5. Architectural Constraints

When building extensions, you MUST obey the following invariants:

*   **No Spontaneous Events:** Every event *must* have a `causal_parent` that currently exists in the `events` table for that `trace_id`. The only exception is `TRACE_START`.
*   **No Backwards Time Travel:** The `timestamp` of an event must be strictly greater than the `timestamp` of its `causal_parent`. Always use `get_next_timestamp()` from the Logical Clock.
*   **No Mutable Payloads:** Once an event is passed to `cap_event_commit`, you must assume it is frozen. Modifying the payload dictionary afterward will break the `state_hash` and corrupt the trace.
*   **Strict Layer Boundaries:**
    *   CLIDE (L4) must never execute shell commands directly. It only creates `INTENT_CREATE` events.
    *   APC-CANNON (L2) must never try to parse goals or understand intent. It only executes exactly what it is told.
    *   PIE (L3) must never alter state or execute commands. It only reads traces.
