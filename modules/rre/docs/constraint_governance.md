# RRE Constraint and Failure Governance

## 1. Constraint Locking
Constraints are irreversible facts. Once the user confirms a constraint (e.g., "The system must run offline"), L2 locks it.
- **Contradiction Detection**: If a future user input contradicts a locked constraint (e.g., "It will pull data from AWS on every click"), L2 triggers a `HALT`.
- **Resolution Protocol**: L1 must explicitly present the contradiction to the user and force them to either revoke the old constraint or modify the new requirement.

## 2. Failure Injection
In `DEEP` mode or `U=4`, L2 generates synthetic failure payloads based on the current architecture:
- **Load Failures**: "What is the behavior when 10,000 concurrent writes hit this specific table?"
- **State Failures**: "If the network drops between Step 2 and Step 3, how does the system recover?"
- **Adversarial**: "How does the system prevent a user from manually altering this client-side state?"

## 3. Determinism Enforcement
A system is not considered complete unless it is deterministic. Every feature must pass the Determinism Checklist:
- [ ] Are all initial states defined?
- [ ] Are all transition triggers explicitly named?
- [ ] Are all failure states and fallback routes mapped?
- [ ] Is the operation idempotent, or does execution order change the outcome?