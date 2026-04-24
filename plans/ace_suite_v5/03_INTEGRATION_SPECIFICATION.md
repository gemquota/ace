# 📡 INTEGRATION SPECIFICATION: THE DECENTRALIZED BUS // v0.1.0

## 1. Decentralized Persistence Responsibility
Each component MUST manage its own persistence layer in the unified database:
- **CLIDE**: Manages the `events` and `traces` tables in `cap_events.db`.
- **APC**: Manages execution artifacts and links them via the `causal_index`.
- **GFS**: Manages the neural graph state via its own substrate-to-DB bindings.
- **GCE (ACE UI)**: Manages UI-specific artifacts (Vault, Chat History) and subscribes to the `live` event bus.

## 2. ACE_EVENT_BUS (Streaming Protocol)
The system uses a **Reactive Projection** model. The UI does not poll; it listens to the `ACE_EVENT_BUS` and updates its local state reactively.
- **Source Filtering**: UI can subscribe to specific sources (e.g., `/ws/subsystem/APC` for real-time diffs).
- **Event Header**: Every event MUST carry the unified `trace_id` and `source` header.

## 3. GFS Causal Branching (Fork & Merge)
- When GFS detects a conflict between its local graph mutation and the remote state, it dispatches a `FORK_REQUEST` to CLIDE.
- CLIDE persists the branch.
- The UI (GCE) receives the `FORK_CREATED` event and prompts the user for a "Manual Reconciliation" via a visual diff interface.

## 4. APC Sandbox Artifacts
- APC executes in a unique sandbox per `trace_id`.
- Diffs are generated between the sandbox state and the **Active Project Root**.
- Diffs are saved as `.patch` files in `data/artifacts/`.
- The URI of the project-level artifact is pushed to the `ACE_EVENT_BUS` for immediate UI rendering and user review.

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
