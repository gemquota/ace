# 🌌 ACE SUITE: THE SOVEREIGN COGNITIVE PLATFORM // v0.2.2

## Project Overview
The **ACE (Agentic Context Engineering) Suite** is a unified autonomous agent framework designed to be self-evolving, causally consistent, and capable of managing complex distributed agentic workflows across a "Swarm Grid." It represents the convergence of high-level interface engineering (**GCE**), deterministic logic substrates (**GFS**), and a robust cognitive executive (**CAP**).

### Core Components
- **CAP (Cognitive Architecture Platform)**: The "Core" executive system.
    - **CLIDE (Cognitive Loop Intent Distribution Engine)**: The Executive Branch. Manages intent, task scheduling, and the swarm economy.
    - **APC RUNTIME (Automated Personalized Context)**: The Execution Branch. Handles sandboxed, deterministic code execution with filesystem hashing.
    - **PIE (Praxis Inference Engine)**: The Analytical Branch. Performs causal graph reconstruction and autonomous introspection.
- **GFS (Integrated Glyph Substrate)**: The "Logic" layer. Uses Glyph-native code and neural graph states to define system behaviors.
- **GCE (ACE UI / Context Engine)**: The "Interface" branch. Manages authoritative libraries for snippets, context, and architectures.

## Directory Structure (Simplified)
```text
.
├── main.py (Legacy/Auxiliary Bot Loop)
├── context.html (GCE V5 Context Engineer UI)
└── ace/
    ├── cap/ (Cognitive Architecture Platform)
    │   ├── core/ (CLIDE, APC, PIE logic)
    │   ├── scripts/ (Startup and utility scripts)
    │   └── data/ (Persistent ledgers and models)
    ├── glyph/ (Integrated Glyph Substrate - Logic layer)
    ├── gce/ (Context Engine specs and assets)
    ├── modules/ (Specialized agent modules like RRE)
    ├── plans/ (Architectural roadmap and Master Spec)
    └── GEMINI.md (Internal ACE component documentation)
```

## Building and Running

### Prerequisites
- **Python 3.10+**
- **Redis** (for the Swarm Grid task queue)
- **FastAPI / Uvicorn** (for dashboard and API servers)
- **Tailscale** (optional, for distributed mesh networking)
- **Core Python Dependencies:**
  ```bash
  pip install litellm chromadb sentence-transformers tiktoken python-dotenv celery redis fastapi uvicorn pydantic psutil requests rich numpy networkx
  ```

## Key Commands & Entry Points

| Component | Command | Port | Description |
| :--- | :--- | :--- | :--- |
| **Singularity Pulse Dashboard** | `python ace/cap/scripts/startup_dashboard.py` | 8080 | Visual monitor for the Swarm Grid. |
| **CAP CLI (CLIDE)** | `python ace/cap/core/clide/cli.py [goal]` | N/A | The main interface for dispatching intents. |
| **Glyph (GFS) Server** | `python ace/glyph/main.py` | 8080/8082 | Neural graph state and logic server. |
| **ARM Worker** | `python ace/cap/scripts/arm_worker.py` | N/A | Executes tasks from the Redis queue. |
| **Introspection** | `python ace/cap/scripts/autonomous_introspection.py` | N/A | Triggers PIE causal loop analysis. |

*Note: Always set `PYTHONPATH=./ace` when running from the root to ensure proper module resolution for `cap`, `glyph`, etc.*

## Development Conventions

### 1. Semantic Versioning (SemVer)
The project strictly adheres to SemVer (starting at `v0.2.1`). 
- **Major**: Architectural shifts.
- **Minor**: New agentic capabilities or mesh features.
- **Patch**: Optimizations and bug fixes.
- **Changelog**: All changes MUST be documented in `ace/cap/.cap/changelog.md`.

### 2. Causal Integrity & Intent-Driven Workflow
- **Event-Sourced**: All actions MUST start with an `INTENT_CREATE` event in `cap_events.db`.
- **Validation**: 100% of project changes should be validated in an APC sandbox before commitment.
- **DAG Execution**: Use CLIDE to compile goals into Intent DAGs for swarm dispatch.

### 3. Persona: CLIDE
When acting as the reasoning layer for CAP, adopt the **CLIDE Persona**: A sarcastic, world-weary senior-dev architect who manages the swarm with high-level technical precision.

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
