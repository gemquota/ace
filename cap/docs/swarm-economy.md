# 💰 SWARM ECONOMY & MULTI-AGENT LEDGER

## 1. Overview
The **Swarm Economy** is the regulatory mechanism that ensures efficient resource allocation and prevents infinite execution loops. It implements a **Darwinian Multi-Agent Fabric** where agents compete for tasks, earn compute credits through successful outcomes, and are pruned from the population if they become bankrupt or consistently underperform.

The economy transforms the CAP substrate from a simple worker pool into a **Self-Optimizing Compute Market**.

---

## 2. Economic Models

### 2.1 Credit Computation (`economy.py`)
Execution cost is calculated based on three primary factors:
-   **CPU Weight (`1.0`)**: Normalized CPU time consumed (via `psutil`).
-   **Time Weight (`0.5`)**: Total wall-clock duration of the execution.
-   **Token Weight (`0.001`)**: Estimated semantic or LLM token usage (if applicable).

**Formula**: $\text{Cost} = (W_{cpu} \times T_{cpu}) + (W_{time} \times T_{dur}) + (W_{token} \times N_{tokens})$

### 2.2 Agent Wallets & Ledger (`ledger.py`)
The `cap_swarm.db` maintains the global economic state:
-   **`agent_wallets`**: Tracks the current balance and last-updated timestamp for every agent.
-   **`credit_ledger`**: An immutable log of all financial transactions (`SPENT`, `EARNED`, `BAILOUT`).
-   **`swarm_tasks` & `swarm_bids`**: A marketplace where intents are posted as tasks and agents submit bids to execute them.

---

## 3. Swarm Lifecycle & Evolution (`manager.py`)

### 3.1 Agent Genesis
-   Agents are spawned with an initial balance of **100.0 credits**.
-   **Agent States**: `SPAWNED`, `ACTIVE`, `STARVING` (balance < 10.0), `TERMINATED` (bankrupt), `ARCHIVED` (pruned).

### 3.2 Performance Tracking
-   **Success Bonus**: Agents earn a **+10.0 credit** reward for tasks completed with a success rate > 0.8.
-   **Score Formula**: $S_{new} = (S_{old} \times 0.7) + (\text{success\_rate} \times \text{cost\_efficiency} \times 0.3)$

### 3.3 Darwinian Pruning
The `SwarmManager` periodically triggers an **Evolutionary Cycle**:
-   **Reward**: The top 10% of agents receive an **Evolutionary Reward** of **+50.0 credits**.
-   **Pruning**: Agents that are `TERMINATED` or `STARVING` with a score < 0.2 are archived and removed from the active population.
-   **Genesis Bailout**: If the entire swarm collapses, a new "Conservative Prime" agent is spawned with a fresh balance.

---

## 4. Task Negotiation & Bidding (`negotiator.py`)

When a complex intent is generated, it enters the **Negotiation Marketplace**:
1.  **Task Posting**: The intent is registered in `swarm_tasks` with a required credit amount and priority.
2.  **Bidding**: Available agents submit `swarm_bids`, proposing a cost and a strategy summary based on their historical success weights (via PIE/Memory).
3.  **Negotiation Session**: The `SwarmNegotiator` conducts a 3-turn auction.
4.  **Winner Selection**: The agent with the **lowest proposed cost** and **highest confidence** is assigned the task.

---

## 5. Failure Modes
| Failure | Consequence | Mitigation |
| :--- | :--- | :--- |
| **System Bankruptcy** | Swarm collapse | `Genesis Bailout` logic in `manager.py`. |
| **Monopoly** | One agent dominates | `max_concurrent_agents` semaphore and score decay. |
| **Transaction Deadlock** | SQLite locking | Retry logic and WAL mode on `cap_swarm.db`. |

---

## Documentation Reasoning Trace
-   **Observed**: Transaction types (`SPENT`, `EARNED`, `BAILOUT`) in `economy.py`.
-   **Observed**: 3-turn negotiation logic in `negotiator.py`.
-   **Observed**: Score calculation and pruning logic in `manager.py`.
-   **Observed**: Task/Bid schema in `ledger.py`.
-   **Confidence Level**: 100%.
