# 🌐 CAP SYSTEM REPORT (PART 2) // v0.2.0

## 3. Directory Tree (CLIDE Kernel to Storage)

*(Continued from Part 1...)*

├── **core/**
│   ├── **clide/**
│   │   ├── **kernel/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the KERNEL module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `clock.py`
│   │   │       *↳ Maintains the Lamport Logical Clock for the CAP system. It ensures that all distributed events across the Swarm Grid are strictly ordered and causally aligned within the immutable ledger.*
│   │   │   ├── `events.py`
│   │   │       *↳ Defines the rigorous schema and validation logic for immutable system events. It ensures every state transition possesses a valid causal parent and conforms to the ledger's integrity constraints.*
│   │   │   ├── `goal_manager.py`
│   │   │       *↳ Handles the parsing and lifecycle tracking of top-level Operator directives. It acts as the bridge between human intent and the underlying DAG compilation engine.*
│   │   │   ├── `governance.py`
│   │   │       *↳ Enforces system-wide constraints and sovereign directives. It ensures that no spawned subprocess or autonomous intent generation loop exceeds the globally configured resource limits or security boundaries.*
│   │   │   ├── `healer.py`
│   │   │       *↳ The auto-remediation module. It consumes diagnostic reports from PIE and attempts to surgically repair corrupted execution states or missing dependencies without requiring a full temporal rollback.*
│   │   │   ├── `identity.py`
│   │   │       *↳ Manages the Genesis Hash anchoring mechanism. It ensures the system's cryptographic identity matches the local environment, triggering a Sovereign Panic if identity spoofing is detected.*
│   │   │   ├── `loop.py`
│   │   │       *↳ The primary execution loop for the CAP Kernel. It orchestrates the continuous tick cycle, processing pending events, flushing the task queue, and triggering PIE analysis on newly committed traces.*
│   │   │   ├── `orchestrator.py`
│   │   │       *↳ The primary CapOrchestrator integration point. It receives high-level goals, initializes new execution traces, invokes the CLIDE compiler to generate IntentDAGs, and submits actions to the Swarm Broker.*
│   │   │   ├── `planner.py`
│   │   │       *↳ Translates high-level Operator directives into structured, multi-step execution plans before passing them to the DAG compiler.*
│   │   │   ├── `replay.py`
│   │   │       *↳ Implements the temporal horizon and rollback mechanisms. It allows the system to rewind to a previous deterministic state by replaying past events and verifying their cryptographic hashes.*
│   │   │   ├── `router.py`
│   │   │       *↳ Handles the internal routing of system events and RPC calls between the isolated subsystems (CLIDE, APC, PIE).*
│   │   │   ├── `scheduler.py`
│   │   │       *↳ The DAG scheduler. It analyzes the causal dependencies of an IntentDAG and dispatches unblocked ActionNodes to the active task queue.*
│   │   │   ├── `syscalls.py`
│   │   │       *↳ Provides low-level system call interfaces for the CAP Kernel. It handles the raw generation of trace IDs and the immediate commitment of immutable events to the SQLite datastore.*
│   │   │   └── `validator.py`
│   │   │       *↳ Enforces structural and cryptographic validation on incoming tasks or configuration payloads before they are admitted to the active system.*
│   │   ├── **memory/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the MEMORY module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `cap_memory.db`
│   │   │       *↳ Local SQLite datastore holding state fragments, event caches, or node-specific swarm ledgers.*
│   │   │   ├── `clide_memory.db`
│   │   │       *↳ Local SQLite datastore holding state fragments, event caches, or node-specific swarm ledgers.*
│   │   │   ├── `consolidation.py`
│   │   │       *↳ Periodically merges fragmented local states or cache artifacts into the permanent event ledger to optimize storage overhead.*
│   │   │   ├── `episode_builder.py`
│   │   │       *↳ Groups raw trace events into higher-level 'episodes' to provide the HybridRetriever with semantically meaningful memory chunks.*
│   │   │   ├── `episodic_index.py`
│   │   │       *↳ Maintains the searchable index of historical execution episodes, enabling rapid memory-augmented reasoning by the CLIDE compiler.*
│   │   │   ├── `retrieval.py`
│   │   │       *↳ Implements the HybridRetriever. It scans historical event traces to find successful execution patterns for specific intents, bypassing static ontologies.*
│   │   │   ├── `semantic_store.py`
│   │   │       *↳ The local vector or structural datastore for holding semantic relationships and previously compiled Intent DAG logic.*
│   │   │   ├── `store.py`
│   │   │       *↳ Generic storage interface providing CRUD abstractions over the underlying SQLite or Redis data layers.*
│   │   │   └── `working_memory.py`
│   │   │       *↳ Maintains the volatile, short-term context of the current execution trace, allowing the Executive branch to make mid-flight adjustments.*
│   │   ├── **meta/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the META module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `evaluator.py`
│   │   │       *↳ Assesses the success or failure of a completed trace, providing the fitness score used by the Meta-Cognition layer for evolution.*
│   │   │   ├── `experiment.py`
│   │   │       *↳ Manages isolated A/B testing of system mutations, ensuring that new architectural configurations do not permanently damage the master ledger.*
│   │   │   └── `model.py`
│   │   │       *↳ Defines the Pydantic data models and validation schemas used for serializing state data and inter-node API communication.*
│   │   ├── **observability/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the OBSERVABILITY module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `aggregator.py`
│   │   │       *↳ Collects distributed telemetry from across the Swarm Grid, synthesizing it into cohesive metrics for the Singularity Pulse dashboard.*
│   │   │   ├── `graph_builder.py`
│   │   │       *↳ Constructs the directed acyclic graphs (DAGs) representing temporal, causal, and entity relationships from the raw event stream.*
│   │   │   ├── `models.py`
│   │   │       *↳ Defines the Pydantic data models and validation schemas used for serializing state data and inter-node API communication.*
│   │   │   ├── `state_builder.py`
│   │   │       *↳ A utility module that reconstructs the holistic system state from the raw, immutable event log for analytical purposes.*
│   │   │   └── `stream_processor.py`
│   │   │       *↳ Ingests the high-throughput real-time event stream from the Swarm Broker, filtering and routing critical events to the appropriate subsystems.*
│   │   ├── `ontology.py`
│   │       *↳ Stores the static Semantic Primitives used by the CLIDE compiler. This dictionary maps high-level concepts (like 'setup_workspace') to specific, verified arrays of shell commands.*
│   │   ├── **openworld/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the OPENWORLD module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `mcp_generator.py`
│   │   │       *↳ Dynamically generates Model Context Protocol (MCP) compatible payloads to interface securely with remote substrates.*
│   │   │   ├── `remote_tunnel.py`
│   │   │       *↳ Establishes and maintains the secure SSH or Tailscale tunnels required for dispatching tasks to foreign nodes in the Swarm Grid.*
│   │   │   └── `x11_bridge.py`
│   │   │       *↳ Provides an interface for interacting with or simulating GUI interactions on execution nodes equipped with X11/display capabilities.*
│   │   ├── `schema.py`
│   │       *↳ Defines the foundational data structures for the Intent compilation process. It contains the Pydantic/dataclass definitions for ActionNodes and IntentDAGs.*
│   │   ├── **sovereign/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the SOVEREIGN module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   └── `engine.py`
│   │   │       *↳ The entry point for the Praxis Inference Engine. It ingests raw event traces from the ledger, verifying causal linkages and detecting corruption.*
│   │   ├── `state_graph.py`
│   │       *↳ Manages the in-memory representation of the execution state graph during an active trace. It tracks which ActionNodes are pending, executing, or completed, ensuring causal dependencies are respected.*
│   │   ├── **storage/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the STORAGE module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   ├── `cap_events.db`
│   │   │       *↳ The master immutable SQLite ledger. Records every INTENT_CREATE and EXEC_COMPLETE event, maintaining the strict temporal horizon.*
│   │   │   ├── `db.py`
│   │   │       *↳ Handles direct SQLite transactions with the master ledger. It ensures that event commits respect causal consistency and maintains integrity.*
│   │   │   └── `schema.sql`
│   │   │       *↳ The database initialization schema. It defines the strict tabular structures for the immutable event ledger, swarm wallets, and causal graph nodes required by SQLite.*
│   │   ├── **swarm/**
│   │   │   ├── `economy.py`
│   │   │       *↳ Enforces the Swarm Economy constraints. It tracks Compute Credits (CR) across distributed agents, ensuring that complex executions are 'paid for'.*
│   │   │   ├── `fitness.py`
│   │   │       *↳ The evolutionary fitness function. It scores the efficiency of the system's current architectural configuration against historical baselines.*
│   │   │   ├── `genome.py`
│   │   │       *↳ Represents the serialized structural parameters (the 'DNA') of the CAP system, which the Autopoietic Loop mutates during evolution.*
│   │   │   ├── `ledger.py`
│   │   │       *↳ Manages the transactional records of the Swarm Broker. It logs the exchange of intents and compute credits during multi-agent negotiation sessions.*
│   │   │   ├── `manager.py`
│   │   │       *↳ Provides lifecycle management and orchestration for the active nodes running within the local host environment.*
│   │   │   └── `negotiator.py`
│   │   │       *↳ The Swarm Economy bidding engine. It allows distributed agents to negotiate compute credit costs before accepting a task from the broker.*
│   │   ├── `task_queue.py`
│   │       *↳ Interfaces directly with the Redis/Celery Swarm Broker to manage the distribution of compiled ActionNodes. It handles task serialization, prioritization scoring, and payload dispatch.*
