# 🌐 CAP SYSTEM REPORT (PART 1) // v0.2.0

## 1. System Asset Overview
The CAP operates in the **DISTRIBUTED_HORIZON** modality utilizing a Redis/Celery Swarm Grid.

## 2. Directory Tree (Root to CLIDE Control)

├── **.cap/**
│   ├── `OPERATOR_GUIDE.md`
│       *↳ The authoritative operational manual for human interaction with CAP. It defines execution workflows, diagnostic protocols for system failures, and the rules for engaging the Autopoietic Loop.*
│   ├── `changelog.md`
│       *↳ The strictly enforced, Semantic Versioning-compliant historical record of the system. It tracks all autopoietic updates, architectural shifts, and capability expansions across the swarm.*
│   └── `operator_manifest.json`
│       *↳ A dynamic JSON registry tracking the active distributed execution nodes in the Swarm Grid. It defines their IP addresses, hardware capabilities (e.g., Windows, Termux), and maximum load limits.*
├── `.capignore`
    *↳ Configuration file defining exclusion patterns for the APC-RUNTIME deterministic hasher. It ensures transient files or logs are not calculated into the pre/post state cryptographic hashes.*
├── `.env`
    *↳ Stores critical environment variables, including the essential 'Genesis Hash' which anchors the system's identity and prevents Sovereign Panics.*
├── `GEMINI.md`
    *↳ The CAP System Superprompt and root orchestrator configuration. It defines the Sovereign Orchestrator persona, mandates Semantic Versioning, and establishes the operational rules for the DISTRIBUTED_HORIZON modality.*
├── `README.md`
    *↳ The primary entry point documentation for the Cognitive Architecture Platform. It provides a high-level overview of the event-sourced epistemology, the core triad architecture, and initial setup instructions.*
├── `VERSION`
    *↳ Contains the strict Semantic Version string (e.g., 0.2.1) defining the current evolutionary state of the CAP ecosystem.*
├── **core/**
│   ├── `.env`
│       *↳ Stores critical environment variables, including the essential 'Genesis Hash' which anchors the system's identity and prevents Sovereign Panics.*
│   ├── `META_PROMPT.md`
│       *↳ The Core Meta-Prompt that defines the interaction protocols between the three architectural pillars (CLIDE, APC, PIE). It establishes the Swarm Execution Loop and distributed communication axioms.*
│   ├── **apc/**
│   │   ├── `__init__.py`
│   │       *↳ Initializes the APC module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   ├── `executor.py`
│   │       *↳ The core execution engine for APC-RUNTIME. Responsible for spawning sandboxed subprocesses, capturing standard output/error streams, and enforcing execution timeouts. It directly interacts with the hasher to record deterministic state transitions.*
│   │   ├── `hasher.py`
│   │       *↳ Implements the deterministic filesystem hashing algorithm used to verify command side-effects. It walks directories, sorts file metadata alphabetically, and generates a SHA-256 digest to ensure execution integrity.*
│   │   ├── `sandbox.py`
│   │       *↳ Manages the creation and teardown of ephemeral, isolated execution environments. It enforces strict security denylists (e.g., preventing path traversal) to ensure autonomous actions do not damage the host system.*
│   │   └── `test_apc.py`
│   │       *↳ Validates the deterministic execution engine, ensuring sandboxed commands correctly produce matching pre/post filesystem cryptographic hashes.*
│   ├── **clide/**
│   │   ├── `GEMINI.md`
│   │       *↳ The CAP System Superprompt and root orchestrator configuration. It defines the Sovereign Orchestrator persona, mandates Semantic Versioning, and establishes the operational rules for the DISTRIBUTED_HORIZON modality.*
│   │   ├── `cli.py`
│   │       *↳ The primary command-line interface for human operators. It parses arguments for initiating new traces, replaying historical events, rolling back states, and invoking PIE's advanced diagnostic/predictive inference modes.*
│   │   ├── `compiler.py`
│   │       *↳ The cognitive core of CLIDE's reasoning engine. It translates ambiguous natural language goals into deterministic IntentDAG structures by mapping requests to predefined semantic primitives or dynamically forging new tools.*
│   │   ├── **control/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the CONTROL module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `anomaly_response.py`
│   │   │       *↳ Defines the system's automated countermeasures when execution vitals drop below acceptable thresholds. It handles the triggering of sovereign panics, trace rollbacks, and PIE Sweeper engagement.*
│   │   │   ├── `controller.py`
│   │   │       *↳ The central feedback controller for the Executive branch. It regulates the flow of tasks into the swarm queue based on current grid load and active node capabilities.*
│   │   │   ├── `explainability.py`
│   │   │       *↳ Generates human-readable rationales for why CLIDE compiled a specific IntentDAG. It translates complex causal dependencies and historical memory weights into understandable execution logs.*
│   │   │   ├── `hitl.py`
│   │   │       *↳ Implements the Human-In-The-Loop (HITL) mechanism. It manages the interruption of autonomous execution flows when a task requires explicit operator permission or violates policy.*
│   │   │   ├── `influence.py`
│   │   │       *↳ Calculates and applies Swarm Economy weights to active intents. It determines the 'Compute Credit' cost of an action based on its historical success rate and current system load.*
│   │   │   ├── `permissions.py`
│   │   │       *↳ Enforces granular access controls over what specific commands or files a generated IntentDAG is allowed to touch, acting as a secondary authorization layer.*
│   │   │   ├── `policy.py`
│   │   │       *↳ Defines the strict operational boundaries for the Executive branch. It ensures that compiled IntentDAGs do not violate core directives or bypass the causal ledger.*
│   │   │   └── `simulation.py`
│   │   │       *↳ Provides a dry-run environment where CLIDE can test the compilation and execution flow of an IntentDAG in a purely virtual state graph before committing actual tasks.*
│   │   ├── **dashboard/**
│   │   │   ├── `server.py`
│   │   │       *↳ The WebSocket server hosting the Singularity Pulse dashboard, streaming real-time metrics and visualization data to the frontend.*
│   │   │   └── **static/**
│   │   │       └── `index.html`
│   │   │           *↳ The primary frontend interface for the Singularity Pulse Canvas. It renders the WebGL nodes, the bio-rhythm margins, and the real-time event waterfall streaming from the WebSocket server.*
