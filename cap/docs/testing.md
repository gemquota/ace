# 🧪 TESTING & VERIFICATION FRAMEWORK

## 1. Overview
The CAP system follows a **Phase-Locked Testing Protocol**. Each evolutionary phase (1 through 20) is guarded by a mandatory integration test that validates the new primitives while ensuring zero regression in the foundational kernel logic.

---

## 2. Test Suite Decomposition

### 2.1 Foundational Tests (Phases 1-10)
-   `test_phase5.py`: Validates the basic Intent → Action → Event → Inference loop.
-   `test_phase6.py`: Verifies the Determinism Engine (Hashing & Replay).
-   `test_phase8.py`: Validates distributed event emission across multiple `node_id`s.
-   `test_phase10.py`: Tests recursive self-modification (code rewriting).

### 2.2 Advanced & Sovereign Tests (Phases 11-20)
-   `test_phase15.py`: Verifies distributed task queueing and worker claiming.
-   `test_phase16.py`: Validates Cognitive Memory persistence and pattern weighting.
-   `test_phase17.py`: Tests autonomous goal generation by the Sovereign Engine.
-   `test_phase18.py`: Validates Meta-Cognitive architecture evaluation and mutation.
-   `test_phase19.py`: Verifies Genesis Hash anchoring and substrate migration triggers.
-   `test_phase20.py`: Tests the Swarm Economy (Credits, Bidding, and Darwinian Pruning).

---

## 3. Core Verification Primitives

### 3.1 Determinism Verification
Tests in `test_phase6.py` and `test_phase19.py` utilize **Filesystem State Assertions**:
1.  Capture `pre_state_hash`.
2.  Execute command.
3.  Capture `post_state_hash`.
4.  Assert that the hash matches the expected side-effect recorded in the trace.

### 3.2 Causal Integrity Verification
Integration tests verify that:
-   Every event has a valid `causal_parent`.
-   Logical clocks are strictly monotonic.
-   `TRACE_START` events are correctly anchored to the Genesis Hash.

---

## 4. Running the Tests
To run the full Phase 20 suite:
```bash
export PYTHONPATH=.
python3 cap/test_phase20.py
```
*Note: Some tests (e.g., Phase 15) spawn background worker processes and require valid SQLite database paths.*

---

## Documentation Reasoning Trace
-   **Observed**: `test_phase*.py` files in the repository.
-   **Observed**: The specific validation logic I implemented for Phases 16-20.
-   **Confidence Level**: 100%.
