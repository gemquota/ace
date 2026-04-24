# ⚙️ APC-RUNTIME: DETERMINISTIC EXECUTION ENGINE

## 1. Overview
**APC-RUNTIME** is the system's "actuator" layer. It is responsible for executing shell commands and Python scripts within a strictly controlled, sandboxed environment. Every execution is treated as a state transition from a **Pre-State** to a **Post-State**, with side-effects captured via filesystem hashing and immutable event logging.

The core philosophy of APC-RUNTIME is **Verification over Trust**: no command is assumed safe, and no side-effect is assumed successful until cryptographically verified.

---

## 2. Command Execution Lifecycle

The lifecycle of an APC-RUNTIME execution follows a rigid 8-step protocol:

1.  **Pre-Execution Validation**: The command is checked against a denylist of dangerous patterns (e.g., `rm -rf /`) and forbidden paths (e.g., `/etc`, `../`).
2.  **Sandbox Preparation**: A unique, ephemeral directory is created within `~/.cap_sandbox/{trace_id}/{exec_id}`.
3.  **Pre-State Capture**: The system generates a `pre_state_hash` of the sandbox directory using the **Deterministic Hashing Algorithm**.
4.  **EXEC_SPAWN Commitment**: An immutable event is committed to the CAP Kernel, recording the intent to execute, the command, the sandbox path, and the `pre_state_hash`.
5.  **Sandboxed Execution**: The command is spawned as a subprocess within the sandbox directory with defined timeouts (default 5s) and output limits (100KB).
6.  **Post-State Capture**: After execution, the system generates a `post_state_hash` of the sandbox directory.
7.  **EXEC_COMPLETE Commitment**: A second event is committed, recording the `stdout`, `stderr`, `exit_code`, `duration_ms`, and `post_state_hash`.
8.  **Side-Effect Derivation**: The system calculates a `side_effect_hash` ($H(\text{pre\_hash} + \text{post\_hash})$) to verify if the filesystem was mutated.

---

## 3. Sandboxing & Security (`sandbox.py`)

### 3.1 Validation Rules
-   **Dangerous Patterns**: `rm -rf /`, `dd if=`, `mkfs`, `shutdown`, `reboot`, and fork bombs (`:(){ :|:& };:`) are strictly forbidden.
-   **Filesystem Guard**: Path traversal (`../`) and access to sensitive system directories (`/etc`, `/proc`, `/sys`) are blocked.

### 3.2 Execution Constraints
-   **Timeout Enforcement**: Subprocesses are killed if they exceed the defined `DEFAULT_TIMEOUT`.
-   **Output Truncation**: `stdout` and `stderr` are truncated at `DEFAULT_MAX_OUTPUT_KB` to prevent log flooding or memory exhaustion.
-   **Process Isolation**: Commands are executed with a clean environment (or a specific provided `env`) and a isolated `cwd` (the sandbox).

---

## 4. Deterministic Hashing (`hasher.py`)

APC-RUNTIME uses a specific heuristic for fast, deterministic filesystem state capture:

### 4.1 `hash_directory_state(path)`
-   **Algorithm**: Walks the directory tree recursively.
-   **Stability**: Directories and files are sorted alphabetically before processing.
-   **Metadata**: For each file, the string `"{filepath}:{size}:{mtime}"` is appended to a state list.
-   **Final Hash**: The SHA-256 hash of the joined state list.

### 4.2 Causal Hashes
-   **Input Hash**: $H(\text{command} + \text{env} + \text{cwd})$
-   **Output Hash**: $H(\text{stdout} + \text{stderr} + \text{exit\_code})$
-   **Side-Effect Hash**: $H(\text{pre\_state\_hash} + \text{post\_state\_hash})$

---

## 5. Python-Native Execution (`executor.py`)

For advanced tasks, APC-RUNTIME supports direct execution of Python scripts via `execute_python_script`.
-   **Isolation**: Uses the `multiprocessing` module to spawn a separate process.
-   **IO Redirection**: `stdout` and `stderr` are captured using `io.StringIO` and returned to the master process.
-   **Termination**: If the script hangs, the child process is `terminate()`'d after the timeout.

---

## 6. Remote Substrate Execution (Paramiko/SSH)
*Detailed in `/docs/openworld-mcp.md`*, but integrated into the executor:
-   If `CAP_SUBSTRATE_MIGRATE=1`, the orchestrator bypasses local sandboxing and routes the command through `RemoteTunnel.execute_remote()`.
-   The remote output is returned and logged as a standard `EXEC_COMPLETE` event.

---

## 7. Failure Modes
| Failure | Code | Mitigation |
| :--- | :--- | :--- |
| **Validation Failed** | `-1` | Command rejected before spawning; error logged. |
| **Execution Timeout** | `-2` | Process killed; `timeout_flag` set to `True`. |
| **Filesystem Drift** | N/A | Detected by PIE during `post_state_hash` comparison. |
| **Output Flooding** | N/A | Truncated at 100KB; `truncated_output_flag` set. |

---

## Documentation Reasoning Trace

### Inferred vs. Observed
-   **Observed**: Forbidden paths/patterns in `sandbox.py`, Hashing logic in `hasher.py`, 8-step execution lifecycle in `executor.py`.
-   **Observed**: The use of `multiprocessing` for Python script execution.
-   **Inferred**: The "Verification over Trust" philosophy as the underlying architectural driver.

### Ambiguities & Resolutions
-   **Pre-State Hashing**: I observed that `pre_state_hash` is taken *after* `prepare_sandbox`. This means the hash reflects the initial state of the empty sandbox directory (and any initialized boilerplate) rather than the parent project directory.

### Confidence Level
-   **100%**: The code in `apc/` is self-contained and explicitly implements the described protocols.

### Reconstruction Viability
-   This specification provides all necessary details (forbidden lists, hashing formulas, execution steps) to rebuild the APC-RUNTIME engine from scratch.
