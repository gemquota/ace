# 🛡️ SECURITY, INTEGRITY & SANDBOXING

## 1. Overview
Security in CAP is not an "add-on" but a structural invariant. The system assumes a hostile substrate and employs multiple layers of protection to ensure **Identity Continuity**, **Execution Safety**, and **Causal Integrity**.

---

## 2. Identity Anchoring: The Genesis Hash
The system's identity is cryptographically tied to its origin via the **Genesis Hash**.
-   **Mechanism**: A SHA-256 hash generated from the first trace ID and a timestamp.
-   **Enforcement**: Stored in both `cap_events.db` and the `.env` file.
-   **Identity Crisis**: If the hashes mismatch, the kernel enters a **Sovereign Panic** state and refuses to commit new events, preventing "Identity Spoofing" or unauthorized database swaps.

---

## 3. Sandbox Enforcement (APC-RUNTIME)
The executor employs a "Deny-by-Default" security posture:

### 3.1 Command Validation
-   **Denylists**: Blocks dangerous primitives like `rm -rf /`, `mkfs`, and fork bombs.
-   **Traversal Protection**: Path traversal (`../`) is strictly forbidden to prevent "Jailbreaking" the sandbox.
-   **System Guard**: Prevents access to `/etc`, `/proc`, `/sys`, and other critical system directories.

### 3.2 Resource Constraints
-   **Timeouts**: Hard kill-switch for hanging processes (default 5s).
-   **Output Truncation**: Limits `stdout`/`stderr` to 100KB to prevent memory exhaustion and log-spam attacks.
-   **Directory Isolation**: Every command runs in an isolated `~/.cap_sandbox` directory unique to that execution.

---

## 4. Causal Integrity & Hash Chains
Every event in CAP is a node in a **Cryptographic Hash Chain**.
-   **Hash Calculation**: `state_hash = SHA256(payload + causal_parent_hash + metadata)`.
-   **Immutability**: Once committed, an event cannot be altered without breaking the hash chain of all subsequent events in the trace.
-   **Verification**: The PIE engine and Replay engine verify the hash chain during ingestion, ensuring the system's "history" has not been tampered with.

---

## 5. Economic & Autonomous Protection
-   **Credit Scarcity**: Agents cannot perform "Spam Attacks" or infinite loops because they must "pay" for compute credits. Bankruptcy leads to immediate termination.
-   **Inactivity Kill-Switch**: On-demand MCP servers autonomously shut down after 5 minutes of inactivity to minimize the attack surface.
-   **Rollback Window**: The 4-hour temporal horizon ensures that any environmental damage or "drift" can be logically reverted to a known stable checkpoint.

---

## Documentation Reasoning Trace
-   **Observed**: Hashing in `events.py` and `hasher.py`.
-   **Observed**: Denylists and timeouts in `sandbox.py`.
-   **Observed**: Genesis anchoring in `identity.py`.
-   **Observed**: Economic constraints in `economy.py` and `manager.py`.
-   **Confidence Level**: 100%.
