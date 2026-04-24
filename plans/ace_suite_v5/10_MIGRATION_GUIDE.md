# 🏗️ MIGRATION GUIDE: THE DECENTRALIZED TRANSITION // v0.2.0

## 1. Overview
This guide covers the transition from standalone GCE V5 and GFS-III components into the unified ACE Suite v0.1.0. The primary focus is the **Decentralization of Persistence** and the migration of the 4 Libraries into the persistent DB.

## 2. Data Migration: The 4-Library Export
The legacy GCE LocalStorage data must be migrated to the `cap_swarm.db` (for libraries) and `cap_events.db` (for history).

### Migration Step (ACE-MIG-01):
A new script `scripts/migrate_v5_to_ace.py` will perform the following mapping:
- **`gce_v5_snips`** → `library_snippets` table (Source for Snippet Bank).
- **`gce_v5_contexts`** → `library_vault` table (Source for Context Vault).
- **`gce_v5_arch_presets`** (if exists) → `library_architecture` table (Source for Architecture Collections).
- **`gce_v5_chats`** → `events` table (Causal reconstruction into Chat History).

## 3. Communication Migration: Event-Bus Adoption
- **Legacy**: UI components using isolated LocalStorage and direct fetch calls.
- **ACE**: UI components subscribing to the `ACE_EVENT_BUS` for real-time state projection.

### Migration Step (ACE-MIG-02):
Update `context.html` (becoming `ui/index.html`) to:
1. Establish a persistent WebSocket connection to `/ws/live`.
2. Initialize local state by fetching the "Full Mesh" from `/api/observability/full_mesh`.
3. Listen for `COGNITIVE_EVENT` and `AGENT_STATE` updates to drive UI reactivity.

## 4. GFS Substrate Migration
- **Legacy**: Substrates (Memory, Telemetry) using in-memory dicts or local JSON files.
- **ACE**: Substrates refactored to use SQLite bindings for `cap_events.db`.

### Migration Step (ACE-MIG-03):
Update `glyph/src/backend/substrates.py` to:
1. Replace `self.storage = {}` with a database connection pool.
2. Implement atomic `save_node()` and `load_graph()` methods using SQL transactions.

## 5. System Boot Order (Unified Launcher)
A new script `scripts/launch_ace_suite.py` will:
1. Start Redis (for Celery/Swarm support).
2. Launch the CLIDE Dashboard Server (`core/clide/dashboard/server.py`).
3. Start the local APC ARM worker node.
4. Launch the ACE UI (`ui/index.html`) via a local web server (FastAPI).

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
