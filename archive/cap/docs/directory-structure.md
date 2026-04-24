# 📂 DIRECTORY STRUCTURE // CAP 3.0.0

The CAP project is organized into a clean, modular hierarchy to separate core logic from data, logs, and maintenance tools.

## 📍 Root: `dev/cap/`

### 🧠 `core/` (The Neural Core)
- **`clide/`**: (Command Line Interface Database)
    - Kernel, Storage logic, Swarm economy, and the Synaptic Dashboard.
- **`apc/`**: (Automated Personalized Context)
    - Command execution, sandboxing, and filesystem state hashing.
- **`pie/`**: (Praxis Inference Engine)
    - Causal reconstruction, diagnostic flavors, and predictive reasoning.
- **`inception/`**: Evolutionary prompt sequences used to build the system.

### 💾 `data/` (Persistence Layer)
- `cap_events.db`: The master immutable event log.
- `cap_swarm.db`: Swarm wallets, intents, and ledger.
- `cap_arch_model.json`: Self-architecture state.
- `pie_model.json`: Causal inference state.

### 📜 `logs/` (Observability)
- `traces/`: Raw execution logs for every trace UUID.
- `crash_backups/`: Historical crash data for post-mortem analysis.
- `sovereign_debug.log`: Global kernel debug output.

### 🛠️ `scripts/` (Utilities)
- `build_apc_real.py`: Core system build/rebuild logic.
- `startup_dashboard.py`: Launch script for the Synaptic IDE.
- `version_manager.py`: Automated version incrementing.
- `generate_report.py`: Market and cognitive vitality reporting.

### 📖 `docs/` (Specifications)
- Technical manuals, evolutionary roadmaps, and UI mockups.
