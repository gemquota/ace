# 📊 DATA MODELS & STORAGE SCHEMA

## 1. Overview
CAP Phase 20 utilizes a multi-layered SQLite storage architecture to maintain the immutable event log, task queue, swarm economy, and cognitive memory. Each database is optimized for its specific role, using **Write-Ahead Logging (WAL)** to support concurrent multi-agent access on Android/Termux.

---

## 2. Core Event Log (`cap_events.db`)

The primary source of truth for all system transitions.

### 2.1 Table: `events`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `event_id` | TEXT | PRIMARY KEY | UUID for the event. |
| `trace_id` | TEXT | REFERENCES `traces` | The cognitive session ID. |
| `node_id` | TEXT | NOT NULL | Originating physical node. |
| `timestamp` | INTEGER | NOT NULL | Wall-clock time (seconds). |
| `logical_clock`| INTEGER | NOT NULL | Lamport timestamp for ordering. |
| `layer` | TEXT | NOT NULL | CLIDE, APC, PXE, CAP. |
| `event_type` | TEXT | NOT NULL | e.g., `EXEC_SPAWN`, `INFER`. |
| `payload` | TEXT | JSON | Event-specific context. |
| `causal_parent`| TEXT | REFERENCES `events` | The direct trigger of this event. |
| `state_hash` | TEXT | NOT NULL | $H(\text{meta} + \text{parent\_hash})$. |

### 2.2 Table: `system_identity`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY (id=1) | Singleton record. |
| `genesis_hash` | TEXT | NOT NULL | The root identity hash. |
| `created_at` | INTEGER | NOT NULL | System birth timestamp. |

---

## 3. Distributed Task Queue

### 3.1 Table: `task_queue`
| Column | Type | Description |
| :--- | :--- | :--- |
| `task_id` | TEXT | Unique ID for the unit of work. |
| `status` | TEXT | `PENDING`, `CLAIMED`, `SUCCESS`, `FAILED`. |
| `node_id` | TEXT | The worker node currently executing the task. |
| `lease_expiry` | INTEGER | Timestamp after which the task is retried. |
| `action_payload`| TEXT | JSON-serialized `ActionNode`. |

---

## 4. Swarm Economy (`cap_swarm.db`)

### 4.1 Table: `agent_wallets`
-   **`agent_id`**: PRIMARY KEY.
-   **`balance`**: REAL (Initial: 100.0).
-   **`last_updated`**: INTEGER.

### 4.2 Table: `swarm_tasks` & `swarm_bids`
-   **`swarm_tasks`**: Stores intents posted for negotiation.
-   **`swarm_bids`**: Stores agent proposals including `proposed_cost` and `confidence`.

---

## 5. Cognitive Memory (`cap_memory.db`)

### 5.1 Table: `command_sequences`
-   **`intent_label`**: Semantic primitive.
-   **`command_sequence`**: JSON list of literal shell commands.
-   **`outcome`**: `success` or `failure`.
-   **`weight`**: Evolutionary score (1.0 default).

### 5.2 Table: `pattern_weights`
-   **`pattern_hash`**: SHA-256 of a command or fragment.
-   **`weight`**: Current reinforcement level.

---

## Documentation Reasoning Trace
-   **Observed**: SQL schema from `schema.sql`.
-   **Observed**: Wallet and ledger schemas in `swarm/economy.py` and `swarm/ledger.py`.
-   **Observed**: Memory schema in `memory/store.py`.
-   **Inferred**: Index strategy (logical clock vs timestamp) for distributed ordering.
-   **Confidence Level**: 100%.
