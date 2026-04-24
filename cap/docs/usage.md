# 🚀 USAGE & OPERATION MODES

## 1. Overview
The CAP (Cognitive Architecture Platform) is operated primarily through the `cap/cli.py` interface. It supports multiple execution modes ranging from direct goal execution to autonomous, multi-agent swarm operations.

---

## 2. Basic Execution
To execute a high-level goal, simply pass the goal string to the CLI:
```bash
python3 cap/cli.py "setup_workspace my_project"
```
-   **Trace ID**: To resume or refer to an existing cognitive session, use the `--trace` flag:
    ```bash
    python3 cap/cli.py "add a README.md" --trace <trace_id>
    ```

---

## 3. Cognitive Analysis & PIE
CAP provides deep-dive analysis into the reasoning and failures of a trace:
-   **Diagnostic**: Explain why a trace failed and get suggested fixes:
    ```bash
    python3 cap/cli.py --pie-diagnose <trace_id>
    ```
-   **Predictive**: See what the system predicts the next steps should be:
    ```bash
    python3 cap/cli.py --pie-predict <trace_id>
    ```
-   **Causal Weights**: Inspect the learned transition probabilities between commands:
    ```bash
    python3 cap/cli.py --pie-causal
    ```

---

## 4. Autonomous & Sovereign Modes
For persistent operation without user input:
-   **Autonomous Loop**: Start the background observer and goal generator:
    ```bash
    python3 cap/cli.py --auto-start <trace_id>
    ```
-   **Autonomous Status**: Check the current state (`OBSERVING`, `EXECUTING`, `IDLE`) of a loop:
    ```bash
    python3 cap/cli.py --auto-status <trace_id>
    ```
-   **Sovereign Health**: Evaluate the global health and governance status:
    ```bash
    python3 cap/cli.py --sovereign-status
    ```

---

## 5. Distributed Swarm Operation (Phase 15+)
CAP can distribute tasks across multiple worker nodes:
-   **Start a Worker**: Run a local or remote worker process:
    ```bash
    python3 cap/cli.py --start-worker --worker-id worker_A
    ```
-   **Execute via Queue**: Dispatch a goal to the first available worker in the swarm:
    ```bash
    python3 cap/cli.py "stress_test_system" --use-queue
    ```
-   **Queue Status**: Monitor task status (`PENDING`, `CLAIMED`, `SUCCESS`) and active workers:
    ```bash
    python3 cap/cli.py --queue-status
    ```

---

## 6. Determinism & Rollback
-   **Replay**: Re-execute a trace and verify filesystem hashes against original events:
    ```bash
    python3 cap/cli.py --replay <trace_id>
    ```
-   **Rollback**: Revert a trace (and logically the environment) to a specific event ID:
    ```bash
    python3 cap/cli.py --rollback <trace_id>,<event_id>
    ```

---

## Documentation Reasoning Trace
-   **Observed**: Argparse configuration in `cli.py`.
-   **Observed**: Usage examples for PIE, Sovereignty, and Distributed modes.
-   **Confidence Level**: 100%.
