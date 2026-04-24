# 🌐 CAP SYSTEM REPORT (PART 3) // v0.2.0

## 4. Directory Tree (CLIDE Tests & Submodules)

*(Continued from Part 2...)*

├── **core/**
│   ├── **clide/**
│   │   ├── `test_kernel.py`
│   │       *↳ Validates the foundational primitives of the CLIDE Kernel, such as Lamport logical clock incrementation and strict adherence to the immutable event schema.*
│   │   ├── `test_phase10.py`
│   │       *↳ Validates Sovereign Intelligence protocols, ensuring the system can safely modify its own architectural code and successfully pass PIE verification checks.*
│   │   ├── `test_phase11.py`
│   │       *↳ Validates the Swarm & Economy Ledger initialization, testing the dynamic creation of agent wallets and the initial allocation of Compute Credits (CR).*
│   │   ├── `test_phase12.py`
│   │       *↳ Validates Intent Marketplace mechanics, ensuring distributed agents can correctly bid on tasks based on their internally calculated historical confidence scores.*
│   │   ├── `test_phase14.py`
│   │       *↳ Validates Darwinian Pruning processes, ensuring that bankrupt or consistently failing agents are safely archived and purged from the active swarm grid.*
│   │   ├── `test_phase15.py`
│   │       *↳ Validates Swarm Grid Redis integrations, ensuring Celery worker nodes correctly consume, execute, and acknowledge tasks across the distributed mesh.*
│   │   ├── `test_phase16.py`
│   │       *↳ Validates Hardened Sovereignty, specifically confirming the HybridRetriever's ability to bypass static compilation ontologies using historical memory sequence hits.*
│   │   ├── `test_phase17.py`
│   │       *↳ Validates Synthetic Intent Generation logic, ensuring CLIDE autonomously synthesizes housekeeping or structural repair intents during idle processing cycles.*
│   │   ├── `test_phase18.py`
│   │       *↳ Validates the Genesis Hash anchoring mechanism, verifying that simulated identity spoofing attempts correctly trigger an immediate Sovereign Panic halt.*
│   │   ├── `test_phase19.py`
│   │       *↳ Validates the 4-hour Temporal Horizon boundaries, ensuring that execution traces exceeding the window are cleanly halted or cryptographically rolled back.*
│   │   ├── `test_phase20.py`
│   │       *↳ Validates the complete Sovereign Horizon state, including proper economic weighting in the PIE causal model and successful completion of autopoietic evolution loops.*
│   │   ├── `test_phase5.py`
│   │       *↳ Validates the Epistemic Foundation layer, ensuring that the 'Intent -> Action -> Event' loop correctly persists causally linked records to the SQLite ledger.*
│   │   ├── `test_phase6.py`
│   │       *↳ Validates Determinism architecture, specifically checking filesystem state hashing (pre/post states) and ensuring that executed commands are strictly idempotent.*
│   │   ├── `test_phase7.py`
│   │       *↳ Validates Adaptive Cognition algorithms, ensuring the system can autonomously mutate intent graphs when it detects failure points during execution.*
│   │   ├── `test_phase8.py`
│   │       *↳ Validates the Distributed CAP framework, testing basic remote procedure calls and verifying Multi-Node state synchronization across the network.*
│   │   ├── `test_phase9.py`
│   │       *↳ Validates Autonomous CAP daemon operations, verifying that background task triggering and queue consumption occur correctly without direct human intervention.*
│   │   ├── **types/**
│   │   │   ├── `__init__.py`
│   │   │       *↳ Initializes the TYPES module namespace, linking underlying logic to the broader CAP ecosystem.*
│   │   │   └── `event_types.py`
│   │   │       *↳ Defines the core enumerations for the event-sourced architecture, explicitly mapping out the allowed Layers and EventTypes used in the master ledger.*
│   │   ├── `watchdog.py`
│   │       *↳ A background daemon module that continuously monitors the health of execution nodes and the Redis broker. It detects stalled processes and node disconnections.*
│   │   └── `worker.py`
│   │       *↳ The foundational worker logic for processing queue items. It defines how a generic worker node attaches to the swarm broker, claims a task, and reports lifecycle events.*
│   ├── `clide_swarm.db`
│       *↳ Local SQLite datastore holding state fragments, event caches, or node-specific swarm ledgers.*
