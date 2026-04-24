# ✅ VALIDATION SPECIFICATION: THE RRP-FORGED SUITE // v0.1.0

## 1. Test Tier Evolution
Validation in the ACE Suite moves beyond unit tests into **Causal Integrity Verification**.

## 2. Technical Validation Tiers

### TIER-1: Semantic Determinism (Triple-Pack)
- **ACE-VAL-01**: Verify that a Glyph string compiles to an AST and IntentDAG with 100% parity.
- **ACE-VAL-02**: Verify that Human-Readable pseudocode can be re-compiled into the same Triple-Pack (LLM-validation).

### TIER-2: Sync Fidelity (Local-First)
- **ACE-VAL-03**: Verify aggressive keystroke/fragment sync latency is < 200ms.
- **ACE-VAL-04**: Simulate a WebSocket disconnection and verify that a "Fork & Merge" event is triggered upon reconnection.

### TIER-3: Execution Isolation (APC Diffs)
- **ACE-VAL-05**: Run an execution in an APC Sandbox and verify that NO files outside the sandbox are modified.
- **ACE-VAL-06**: Verify that the generated `.patch` artifact accurately represents the changes made within the sandbox.

### TIER-4: Introspection Accuracy (PIE)
- **ACE-VAL-07**: Inject a synthetic failure into the GFS graph and verify that PIE identifies the correct "Inferred Failure Node."
- **ACE-VAL-08**: Verify that PIE "Scoring" correctly identifies low-relevance events for janitorial pruning.

## 3. Visual Optimism Success Metrics
- **Reversion Speed**: Ghost/Snap-back animations must trigger within 100ms of an `ANOMALY_DETECTED` event.
- **UI Persistence**: 100% of LocalStorage state must be recoverable from the `cap_events.db` after a full cache wipe.

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
