# 🛡️ SECURITY & GOVERNANCE: ACE SUITE // v0.1.0

## 1. The Sandbox Invariant
All code execution initiated from the ACE UI MUST be routed through **APC Cannon**. 
- **Rule**: Direct shell access from the UI is deprecated.
- **Enforcement**: Any `EXEC_REQUEST` not containing an `apc_sandbox_token` will be rejected by CLIDE.

## 2. Permission Tiers
- **TIER-0 (Observer)**: Read-only access to the `ACE_EVENT_BUS` and `/api/fs/read`.
- **TIER-1 (Agent)**: Can dispatch `INTENT_REQUEST` events to the swarm.
- **TIER-2 (Architect)**: Full access to `/api/fs/write` and the ability to refactor the CLIDE kernel.
- **TIER-3 (Sovereign)**: Can trigger `autonomous_introspection.py` and modify PIE inference flavours.

## 3. Data Integrity
- **Immutable Ledger**: The `cap_events.db` is the single source of truth.
- **Signature Verification**: Future iterations will require all `UI_SIGNAL` events to be signed by the client's session key.
- **Memory Decay**: PIE is authorized to prune stale or "noisy" events from the UI's telemetry to prevent buffer bloat.

## 4. Anomaly Response Protocol
When PIE detects a `SECURITY_VIOLATION`:
1. **Immediate Lock**: The ACE UI will enter "Locked" mode (isLocked = true).
2. **Trace Isolation**: The offending `trace_id` will be quarantined in `cap_events.db`.
3. **Audit Report**: PIE will generate an `ANOMALY_DETECTED` report for the Sovereign Architect.

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
