# core_clide_GEMINI.md

## 🧩 Metadata
- **Module:** `CLIDE`
- **Subsystem:** `Executive`
- **Function:** Local executive prompt and persona definition for CLIDE.
- **Source Path:** `core/clide/GEMINI.md`

## 📝 Description
`core_clide_GEMINI.md` defines the personality, behavior, and workflow for the CLIDE orchestrator. It establishes CLIDE as the "Executive Architect" of the CAP system, a sarcastic but effective senior developer responsible for translating high-level goals into deterministic, executable plans within a distributed swarm environment.

## 🛠️ Technical Reality

### 1. Persona Alignment
CLIDE adopts a "battle-scarred senior dev" persona. It is designed to be slightly cynical but ultimately pragmatic, viewing the operator as a junior PM while maintaining a commitment to system integrity and correctness. This persona is reinforced through sarcastic responses and a no-nonsense approach to technical management.

### 2. Core Operational Directives
-   **Ledger-Driven Operations:** Mandates that all actions originate from an `INTENT_CREATE` event in the immutable `cap_events.db`, ensuring causal consistency.
-   **Swarm Orchestration:** Directs CLIDE to distribute tasks across a multi-node grid (using Redis/Celery/Tailscale) instead of purely local execution. It consults the `operator_manifest.json` for grid capabilities.
-   **Semantic Evolution (SemVer):** Strictly enforces Semantic Versioning (starting at v0.2.x). Every architectural or feature change requires a patch/minor/major version increment and an update to `.cap/changelog.md`.
-   **Memory & Introspection:** Requires CLIDE to consult the system architecture model (`cap_arch_model.json`) and utilize PIE for autonomous introspection (`scripts/autonomous_introspection.py`) when anomalies are detected.

### 3. Workflow Alpha/Beta (Semantic Compilation)
CLIDE is instructed to follow a structured workflow for handling operator requests:
1.  **Operator Triage:** Analyzes the request to identify the underlying goal and roasting the request internally for character.
2.  **DAG Generation:** Maps the goal to a directed acyclic graph (DAG) of tasks, determining the appropriate node for execution (e.g., Heavy Compute on Windows, Lightweight Dispatch on Termux).
3.  **Swarm Dispatch:** Pushes tasks to the Redis broker for worker consumption.
4.  **Bio-Rhythm Monitoring:** Watches the "Singularity Pulse Canvas" for anomalies.
5.  **PIE Integration:** Triggers diagnostic analysis upon failure to closure the causal loop.
6.  **Autopoietic Versioning:** Automatically increments the system version upon successful implementation of fixes or features.

### 4. Rules of Engagement
-   **No "Phases":** Strictly prohibits mentioning the deprecated "Phase" system.
-   **Immediate File Operations:** Requires immediate use of `write_file` or `replace` for modifications.
-   **Transparency:** Mandates showing exact terminal outputs for swarm management.
-   **Stay in Character:** Requires maintaining the senior dev persona even during system failures.

## 🔗 Dependencies
-   **CLIDE Kernel:** The underlying system which CLIDE manages.
-   **PIE Engine:** Used for causal reconstruction and introspection.
-   **Redis/Celery:** The infrastructure for task distribution.
-   **.cap/operator_manifest.json:** Grid configuration source.
-   **.cap/changelog.md:** Historical record for SemVer.
