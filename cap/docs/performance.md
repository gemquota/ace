# ⚡ PERFORMANCE & SCALING CHARACTERISTICS (PHASE 20)

## 1. System Bottlenecks & Design Trade-offs
CAP Phase 20 is a **Resilient-First** architecture. It explicitly prioritizes cryptographic integrity, causal traceability, and economic regulation over raw execution throughput.

### 1.1 Filesystem Hashing (APC-RUNTIME)
The primary performance sink remains the **Deterministic State Capture** (`hash_directory_state`).
-   **Overhead**: Before and after every command, the system performs an `os.walk` to generate `pre_state_hash` and `post_state_hash`.
-   **Complexity**: $O(N)$ where $N$ is the number of files in the sandbox.
-   **Mitigation**: Phase 20 employs **Spatial Sandboxing**. By restricting execution to a dedicated `~/.cap_sandbox` directory, the number of files hashed is bounded by the specific task's scope, rather than the entire project.

### 1.2 Multi-Agent Graph Complexity (PIE)
As the swarm grows, the **Causal Graph** complexity increases.
-   **Scaling**: With multiple agents branching traces (Phase 20 `spawn_agent_trace`), PIE must process non-linear, concurrent timelines.
-   **Memory Usage**: NetworkX graphs (`g_event`, `g_causal`) are stored in RAM. A trace with > 5,000 events can consume significant memory on mobile/Android substrates.
-   **Mitigation**: **Trace Segmenting**. The system encourages short, goal-oriented traces. Long-running autonomous loops are encouraged to "re-base" onto new traces periodically.

### 1.3 Database Contention (SQLite WAL)
Concurrent agents and background loops compete for database locks.
-   **The Issue**: Swarm agents, the autonomous loop, and the observability dashboard all access `cap_events.db` and `cap_swarm.db` simultaneously.
-   **Optimization**: All CAP databases are initialized with **PRAGMA journal_mode=WAL** (Write-Ahead Logging). This allows multiple readers and one writer to operate without blocking, which is critical for the Phase 20 multi-agent fabric.

---

## 2. Economic Scaling & Darwinian Pressure
The **Swarm Economy** introduces a new performance dimension: **Resource Efficiency**.

-   **Credit Throttling**: The economy prevents "Resource Exhaustion Attacks" or runaway loops. An agent that executes too many failing commands will go bankrupt and be pruned, freeing up CPU/Memory for higher-performing agents.
-   **Selection Pressure**: By rewarding success (+10.0) and penalizing failure (-20.0), the system naturally converges on the most compute-efficient strategies (shortest command sequences with highest success rates).

---

## 3. Substrate Performance (Remote vs. Local)
The **Substrate-Agile** execution model allows CAP to bypass local performance limits:
-   **Local Limit**: Termux/Android environments are CPU and Thermal constrained.
-   **Offloading**: When `CAP_SUBSTRATE_MIGRATE=1`, heavy tasks (compilation, deep analysis) are routed via SSH.
-   **Latency**: Remote execution adds network latency (~50-200ms) but provides a massive increase in raw compute power, resulting in a net gain for "high-weight" intents.

---

## 4. Architectural Trade-offs Summary

| Metric | Phase 20 Status | Justification |
| :--- | :--- | :--- |
| **Integrity** | Absolute | Every action is hashed, logged, and economically audited. |
| **Latency** | Medium | Sandboxing and WAL mode mitigate the overhead of hashing and DB locks. |
| **Scaling** | Horizontal | Swarm agents can scale across local threads or remote nodes. |
| **Reliability** | High | 4-hour temporal horizons and autonomous healing allow for recovery from drift. |

---

## Documentation Reasoning Trace
-   **Observed**: SQLite WAL mode in `remote_tunnel.py` and implementation in `db.py`.
-   **Observed**: Economic pruning in `manager.py` as a performance regulator.
-   **Observed**: Substrate migration logic in `loop.py` and `orchestrator.py`.
-   **Confidence Level**: 100%.
