# 🌐 CAP SYSTEM REPORT (PART 4) // v0.2.1

## 5. Directory Tree (PIE, Data, and Scripts)

*(Continued from Part 3...)*

├── **core/**
│   └── **pie/**
│       ├── `__init__.py`
│           *↳ Initializes the PIE module namespace, linking underlying logic to the broader CAP ecosystem.*
│       ├── `engine.py`
│           *↳ The entry point for the Praxis Inference Engine. It ingests raw event traces from the ledger, verifying causal linkages and detecting corruption.*
│       ├── **flavours/**
│       │   ├── `causal.py`
│       │       *↳ The causal weighting flavor. It isolates transition matrices to determine the statistical likelihood that one action causally forces another within the Swarm Grid.*
│       │   ├── `core.py`
│       │       *↳ The foundational base classes for PIE flavors. It defines the abstract interfaces required for plugging new analytical models into the inference engine.*
│       │   ├── `diagnostic.py`
│       │       *↳ The diagnostic inference module. It scans traces for failed commands, heuristically mapping stderr outputs to probable root causes and fixes.*
│       │   ├── `introspection.py`
│       │       *↳ Implements the analytical improvement flavor. It recursively analyzes failure clusters to propose overarching architectural paradigms shifts.*
│       │   ├── `neural_alignment.py`
│       │       *↳ An advanced inference flavor that attempts to align the system's serialized behavioral genome with deeper, non-linear patterns detected in the event ledger.*
│       │   └── `predictive.py`
│       │       *↳ The predictive forecasting module. It utilizes causal weights to anticipate the next logical action, allowing preemptive resource caching.*
│       ├── `graph.py`
│           *↳ Utilizes NetworkX to reconstruct multidimensional representations of an event trace, building temporal, causal, and entity graphs.*
│       ├── `inference.py`
│           *↳ Orchestrates the analytical diagnostic and predictive models, leveraging historical trace data to predict actions and detect anomalies.*
│       ├── `reasoning.py`
│           *↳ Houses the advanced logical deduction algorithms, mapping abstract execution failures to specific environmental root causes.*
│       ├── `test_phase13.py`
│           *↳ Validates Praxis Inference Engine (PIE) integration, ensuring raw event streams are correctly reconstructed into Temporal and Causal network graphs.*
│       └── `test_pie.py`
│           *↳ Unit testing suite for the PIE system. Validates graph generation integrity and the accuracy of diagnostic failure mappings.*
├── `dashboard_server.log`
    *↳ An archival telemetry log file. It contains the raw, unparsed stderr/stdout streams from previous autonomous introspection loops or dashboard server crashes.*
├── **data/**
│   ├── `cap_arch_model.json`
│       *↳ The system's internal self-model. Contains meta-metrics regarding system health, historical failure rates, and evolving causal weights.*
│   ├── `cap_events.db`
│       *↳ The master immutable SQLite ledger. Records every INTENT_CREATE and EXEC_COMPLETE event, maintaining the strict temporal horizon.*
│   ├── `cap_swarm.db`
│       *↳ Local SQLite datastore holding state fragments, event caches, or node-specific swarm ledgers.*
│   ├── `clide_events.db`
│       *↳ A specialized local database used by the CLIDE compiler to cache intermediate DAG nodes and semantic mappings.*
│   ├── `combined.txt`
│       *↳ A compiled artifact containing the flattened contents of the system's documentation and operational history, typically used for rapid LLM context injection.*
│   ├── `pie_model.json`
│       *↳ The serialized state of the Praxis Inference Engine's learning weights, tracking command transition frequencies.*
│   └── `sovereign_debug.log`
│       *↳ Diagnostic log file capturing the internal decision-making processes and synthetic intent generation logs of the Sovereign Engine.*
├── **docs/**
│   ├── `apc-runtime.md`
│       *↳ Architectural documentation detailing the Deterministic Execution Engine, sandboxing constraints, and the cryptographic pre/post-state hashing formulas.*
│   ├── `architecture.md`
│       *↳ The macro-level specification of the 10-subsystem CAP architecture, tracking its evolution from Epistemic Foundations to the DISTRIBUTED_HORIZON modality.*
│   ├── `autopoietic-history.md`
│       *↳ A narrative and technical record of the system's self-evolution cycles, logging how autonomous introspection has restructured the DAGs over time.*
│   ├── `build-system.md`
│       *↳ Technical guidelines explaining the configuration of the Mesh State and how local versus remote execution boundaries are defined.*
│   ├── `clide.md`
│       *↳ Architectural documentation for the Cognitive Loop Intent Distribution Engine, explaining semantic compilation, DAG schemas, and ontology mapping.*
│   ├── `compiler.md`
│       *↳ Deep-dive specification into how ambiguous natural language requests are parsed, tokenized, and mapped to executable deterministic primitives.*
│   ├── `dashboard.md`
│       *↳ UI/UX documentation outlining the visual language of the Singularity Pulse, including the meaning of specific ANSI fading colors and bio-rhythm warnings.*
│   ├── `directory-structure.md`
│       *↳ A historical index explaining the rationale behind the tri-pillar folder structure and data separation layers.*
│   ├── `execution-model.md`
│       *↳ Detailed explanation of the Swarm Grid execution pipeline, covering the Celery task queue, Redis broker negotiations, and Worker lifecycles.*
│   ├── `extensibility.md`
│       *↳ Guidelines for forging new tools or adding new Python submodules to the CAP ecosystem without violating the strict causal ledger invariants.*
│   ├── `future.md`
│       *↳ A living roadmap document containing theoretical architectural shifts, such as multi-modal vision models or neural-aligned inference integrations.*
│   ├── `glossary.md`
│       *↳ The master dictionary of CAP-specific terminology, defining critical concepts like Sovereign Panics, Lamport Clocks, and Genesis Hashes.*
│   ├── `healer-rollback.md`
│       *↳ Technical specifications for the temporal horizon mechanism, explaining how the system surgically rewinds the ledger when causal graphs become corrupted.*
│   ├── `inference.md`
│       *↳ Documentation detailing the Praxis Inference Engine (PIE), covering the mathematical models behind diagnostic tracing and predictive causal weighting.*
│   ├── `kernel.md`
│       *↳ The architectural definition of the CAP Kernel, the central arbiter of the immutable event bus and the Lamport logical clock.*
│   ├── `launcher_variants.md`
│       *↳ Historical documentation tracking the evolution of the CLI bootstrapper from basic scripts to the v3.3.2 high-fidelity terminal.*
│   ├── `memory.md`
│       *↳ Specifies the HybridRetriever mechanisms, detailing how the system bypasses static ontologies by accessing episodic memories of successful historical executions.*
│   ├── `meta-cognition.md`
│       *↳ Documentation of the system's self-awareness layer, explaining how it evaluates its own structural fitness and schedules autonomous optimization passes.*
│   ├── `ontology.md`
│       *↳ The manual detailing the baseline semantic primitives, providing examples of how high-level intents map to precise shell command arrays.*
│   ├── `openworld-mcp.md`
│       *↳ Specification for the Model Context Protocol (MCP) integration, defining how CLIDE negotiates execution boundaries on foreign nodes via SSH or Tailscale.*
│   ├── `orchestration.md`
│       *↳ Details the lifecycle of a high-level goal, from Operator ingestion through the DAG compiler, into the Swarm Broker, and out to the APC workers.*
│   ├── `performance.md`
│       *↳ Metrics and benchmarking documentation tracking the latency of event commitments, Redis queue throughput, and PIE inference speeds.*
│   ├── `pie.md`
│       *↳ High-level documentation for the Praxis Inference Engine, serving as an entry point for understanding the triad's analytical branch.*
│   ├── `roadmap.md`
│       *↳ The chronological planning document tracking completed epochs and defining the immediate technical milestones required for full Autopoietic sovereignty.*
│   ├── `schema.md`
│       *↳ Data structure documentation outlining the precise JSON schemas, Pydantic models, and SQLite column types required for inter-node Swarm communication.*
│   ├── `scripts.md`
│       *↳ An index of the utility layer, providing usage instructions for the various reporting, bootstrapping, and optimization scripts in the repository.*
│   ├── `security.md`
│       *↳ The central security policy outlining sandbox restrictions, denylisted shell commands, and the identity spoofing defenses built around the Genesis Hash.*
│   ├── `sovereign.md`
│       *↳ Documentation of the autonomous Sovereign Engine, detailing the conditions under which CAP is allowed to generate its own intents without Operator input.*
│   ├── `swarm-economy.md`
│       *↳ Explains the internal compute credit (CR) marketplace, detailing how agents bid on tasks, earn currency for successful executions, and face Darwinian pruning for failures.*
│   ├── `testing.md`
│       *↳ Guidelines for writing unit tests within the CAP ecosystem, enforcing the requirement that all tests must validate deterministic causal linkages.*
│   ├── `ui-engine.md`
│       *↳ Technical details regarding the Rich library integrations and terminal canvas rendering loops used by the Singularity Pulse dashboard.*
│   ├── `ui-evolution.md`
│       *↳ A historical log tracking the visual shift from standard CLI output to holographic, multi-threaded terminal interfaces.*
│   ├── `usage.md`
│       *↳ A quick-start guide for Operators, explaining the basic CLI commands required to inject goals, query traces, or trigger PIE diagnostics.*
│   └── `worker-queue.md`
│       *↳ Detailed specification of the Redis/Celery queue architecture, covering message serialization, active node polling intervals, and acknowledgment protocols.*
├── **logs/**
│   └── `introspection.log.bak`
│       *↳ An archival telemetry log file. It contains the raw, unparsed stderr/stdout streams from previous autonomous introspection loops or dashboard server crashes.*
├── **reports/**
│   ├── `report_1775884369.md`
│       *↳ A statically generated, time-stamped system report containing snapshots of Swarm Grid vitals, causal decay metrics, and execution latency logs.*
│   └── `report_1775892293.md`
│       *↳ A statically generated, time-stamped system report containing snapshots of Swarm Grid vitals, causal decay metrics, and execution latency logs.*
└── **scripts/**
    ├── `arm_worker.py`
        *↳ The Automated Resource Manager (ARM) daemon. Runs on remote execution nodes, polling the Celery queue and executing tasks locally.*
    ├── `autonomous_introspection.py`
        *↳ The Sweeper Agent execution script. Periodically ingests trace data, triggers PIE's introspection, and dynamically applies structural repairs.*
    ├── `build_apc.py`
        *↳ Legacy build script for the local APC execution environment. Retained for local-only fallback execution.*
    ├── `build_apc_real.py`
        *↳ Transitional build script bridging the local execution sandbox with real host-level pathing logic.*
    ├── `build_mesh_state.py`
        *↳ Configures networking and state prerequisites for the DISTRIBUTED_HORIZON modality, establishing Redis broker connections.*
    ├── `concatenate_docs.py`
        *↳ Utility script to stitch together the modular Markdown documentation into a single contiguous file.*
    ├── `generate_report.py`
        *↳ A utility script that compiles system vitals and swarm economy metrics into human-readable Markdown reports.*
    ├── `install_watchdog.sh`
        *↳ Shell script to install and register the CLIDE watchdog daemon as a background system service.*
    ├── `launch_v3_2_0.py`
        *↳ Legacy bootstrapper script for a previous specific evolutionary phase of the CAP system, retained for rollback testing.*
    ├── `launch_v3_3_2.py`
        *↳ Bootstrapper script for the v3.3.2 dashboard and environment initialization prior to the Semantic Versioning shift.*
    ├── `run_optimization.py`
        *↳ Executes a manual pass of the PieModelEngine to prune decaying causal weights and rebalance the credit ledger.*
    ├── `startup_dashboard.py`
        *↳ Initializes the Singularity Pulse Canvas interface, starting the local WebSocket server for live telemetry streaming.*
    ├── `update_apc_docs.py`
        *↳ Utility script that dynamically updates the APC-RUNTIME documentation based on the latest deterministic hashing rules.*
    ├── `update_apc_reports.py`
        *↳ Utility script that generates diagnostic integrity reports specifically for the APC execution layer.*
    └── `version_manager.py`
        *↳ Automates strict Semantic Versioning workflows. Safely bumps version numbers and appends autopoietic system updates to the changelog.*
