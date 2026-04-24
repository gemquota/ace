# 👑 SOVEREIGN ENGINE & AUTONOMOUS GOAL GENERATION

## 1. Overview
The Sovereign Engine is the seat of the system's agency. It enables CAP to operate without direct user intervention by monitoring the system's state, detecting anomalies, and autonomously generating goals to maintain system health, optimize performance, or explore the environment.

The Sovereign Engine transforms CAP from a **Tool** into an **Agent**.

---

## 2. Core Mechanisms (`engine.py`)

### 2.1 Goal Structure (`Goal`)
An autonomous goal is a structured object containing:
-   **Primitive**: The CLIDE intent primitive to use.
-   **Goal**: The natural language goal string.
-   **Reason**: The trigger (e.g., `ANOMALY_CLUSTER`, `SYSTEM_IDLE`).
-   **Priority & Utility**: Floating-point scores (0.0 to 1.0) used for selection.
-   **Risk**: The potential danger of the goal (e.g., data loss risk).

### 2.2 Goal Generation Triggers
The engine monitors the `InferenceState` from PIE to identify generation opportunities:
1.  **Anomaly Clusters**: If PIE detects `HISTORICAL_FAILURE_MATCH` or repeated failures, the engine generates a high-priority (`0.9`) goal: `fix_repeated_failures`.
2.  **Optimization**: If a trace has many commands (> 5), it generates a goal to `find_redundant_files` or optimize paths.
3.  **Idle Exploration**: If the system is healthy (success rate > 0.9) and idle, it generates low-priority exploration goals like `verify_system_integrity`.
4.  **Meta-Goals**: Receives goals from the Meta-Cognition layer (e.g., `diagnose_apc`, `stress_test_planner`).

---

## 3. The Autonomous Lifecycle (`loop.py`)

The Sovereign Engine operates within the **Autonomous Loop**:

1.  **Observation**: PIE analyzes the current event stream.
2.  **Drift Detection**: The loop identifies "System Drift" (failure clusters or low success rates).
3.  **Goal Generation**: The Sovereign Engine populates a priority queue (Heap) with new goals.
4.  **Goal Selection**: The highest-priority goal is popped and committed as a `GOAL_SELECTED` event.
5.  **Execution**: The orchestrator is invoked to achieve the goal.
6.  **Outcome Reporting**: The result (success rate) is reported back to the Sovereign Engine to refine future generation strategies.

---

## 4. Selection Logic
The engine uses a **Max-Heap** for goal selection, ensuring that critical self-healing tasks (Priority 0.9) always preempt routine optimization or exploration. In Phase 20, selection also considers **Economic Utility**—goals that are expected to yield higher credit rewards (Utility) are favored.

---

## 5. Security & Safety (Sovereign Guard)
To prevent "Runaway Sovereignty":
-   **Risk Thresholds**: Goals with high `risk` scores (e.g., code mutation) require higher `utility` to be selected.
-   **Trace Anchoring**: Every autonomous goal is causal-parented to a `SYSTEM_STATE` event, ensuring the "reasoning" for the goal is always audit-ready.

---

## Documentation Reasoning Trace
-   **Observed**: Heap-based goal queue in `engine.py`, Priority/Utility/Risk fields.
-   **Observed**: Integration with the `AutonomousLoop` in `loop.py`.
-   **Observed**: Trigger logic based on `InferenceState` flags (Anomaly, Success Rate).
-   **Confidence Level**: 95% (Risk thresholding is logic-implied by the `risk` field).
