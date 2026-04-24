# 🌌 ACE Suite: The Sovereign Cognitive Platform // v0.2.2

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)](./ace/cap/.cap/changelog.md)
[![Architecture: CAP/GFS/GCE](https://img.shields.io/badge/Architecture-CAP%20%7C%20GFS%20%7C%20GCE-purple.svg)](#architecture)

The **ACE (Agentic Context Engineering) Suite** is a unified autonomous agent framework designed for self-evolution, causal consistency, and distributed swarm orchestration. It merges high-level interface engineering with deterministic logic substrates and a robust cognitive executive.

---

## 🗺️ Project Overview

The ACE Suite is not just a bot; it's a **Cognitive Architecture**. It manages complex, multi-node agentic workflows across a "Swarm Grid," ensuring that every action is causally linked and every intent is deterministically executed.

### Core Pillars
*   **CAP (Cognitive Architecture Platform):** The "Core" executive system.
*   **GFS (Integrated Glyph Substrate):** The "Logic" layer (Glyph-native code & neural graph states).
*   **GCE (ACE UI / Context Engine):** The "Interface" branch for context management.

---

## 🏗️ Architecture Detail

### 1. CAP: The Brain (Executive)
Located in `ace/cap/`, this is the cognitive heart of the system.
*   **CLIDE (Cognitive Loop Intent Distribution Engine):** The Executive Branch. Handles syscalls, task scheduling, and the swarm economy.
*   **APC RUNTIME (Automated Personalized Context):** The Execution Branch. Provides sandboxed, deterministic code execution with filesystem hashing.
*   **PIE (Praxis Inference Engine):** The Analytical Branch. Performs causal graph reconstruction and autonomous introspection via the "Sweeper Agent."

### 2. GFS: The Substrate (Logic)
Located in `ace/glyph/`, GFS uses a specialized visual-logic language (Glyphs) to define system behaviors. It operates as a logic substrate that the CAP system can manipulate and evolve.

### 3. GCE: The Interface (Context)
Located in `ace/gce/`, GCE manages authoritative libraries for snippets, context, and architectures. It includes the **Singularity Pulse Dashboard** for real-time visualization of the Swarm Grid.

---

## 🚀 Getting Started

### Prerequisites
*   **Python 3.10+**
*   **Redis** (Required for the Swarm Grid task queue)
*   **Tailscale** (Optional, for distributed mesh networking)

### Installation
1.  **Clone the Repository:**
    ```bash
    git clone git@github.com:gemquota/ace.git
    cd ace
    ```

2.  **Install Core Dependencies:**
    ```bash
    pip install litellm chromadb sentence-transformers tiktoken python-dotenv celery redis fastapi uvicorn pydantic psutil requests rich numpy networkx
    ```

3.  **Bootstrap ACE:**
    ```bash
    bash ace/cap/scripts/setup_gemini_skills.sh
    ```

---

## ⚙️ Operational Guide

### 1. Set Module Path
Always run from the project root and ensure the module resolution is set:
```bash
export PYTHONPATH=./ace
```

### 2. Start Core Services (Separate Terminals)
| Component | Command | Port |
| :--- | :--- | :--- |
| **Singularity Pulse** | `python cap/scripts/startup_dashboard.py` | 8080 |
| **Glyph Logic Server** | `python glyph/main.py` | 8082 |
| **ARM Worker** | `python cap/scripts/arm_worker.py` | N/A |

### 3. Dispatch Intents
Use the CLIDE CLI to send high-level goals to the system:
```bash
python cap/core/clide/cli.py "Optimize the swarm economy for low-latency nodes"
```

---

## 🛠️ Development Conventions

### 1. Semantic Versioning (SemVer)
We strictly adhere to SemVer. 
*   **Major (v1.x.x):** Architectural shifts.
*   **Minor (v0.2.x):** New agentic capabilities or mesh features.
*   **Patch (v0.2.2):** Optimizations and bug fixes.
*   **Changelog:** All changes MUST be documented in `ace/cap/.cap/changelog.md`.

### 2. Causal Integrity
*   **Event-Sourcing:** Every action starts with an `INTENT_CREATE` event in `cap_events.db`.
*   **Validation:** 100% of project changes are validated in an APC sandbox before commitment.
*   **Causal Reversion:** The system uses "Visual Optimism" but reverts UI state if backend invariants are violated.

### 3. The CLIDE Persona
When contributing to the reasoning layer, adopt the **CLIDE Persona**: A battle-scarred, sarcastic senior-dev architect. 
> *"Oh great, another intent... I'll just queue that for the Windows node while I wait for Redis to stop complaining."*

---

## 📂 Directory Map
```text
.
├── ace/
│   ├── cap/           # Cognitive Architecture Platform (The Brain)
│   │   ├── core/      # CLIDE, APC, PIE logic
│   │   ├── scripts/   # Startup, introspection, and workers
│   │   └── data/      # SQLite ledgers and model states
│   ├── glyph/         # Integrated Glyph Substrate (The Logic)
│   ├── gce/           # ACE UI / Context Engine (The Interface)
│   ├── modules/       # Specialized agent modules (RRE, etc.)
│   └── plans/         # Master Specification and Roadmaps
├── context.html       # GCE V5 Management UI
├── GEMINI.md          # Internal system documentation
└── README.md          # You are here
```

---

## 🤝 Contributing
1.  Check the `ace/plans/` directory for the latest Roadmap.
2.  Ensure all changes include a trace in `cap_events.db`.
3.  Respect the Triple-Pack Nucleus: Every behavior must be Glyph-Native, AST-represented, and IntentDAG-compatible.

---

*Verified by the RRP-forged ACE Sovereign Orchestrator.*
