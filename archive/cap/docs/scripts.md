# 🛠️ SCRIPTS & UTILITIES

The `dev/cap/scripts/` directory contains tools for managing the lifecycle, observability, and maintenance of the CAP 3.0.0 system.

## 🚀 Deployment & Build

### `build_apc_real.py`
The primary build engine. It compiles the CLIDE ontology, validates the core namespaces, and ensures the data directory is initialized.
**Usage:** `python scripts/build_apc_real.py`

### `startup_dashboard.py`
Convenience script to launch the FastAPI server for the Synaptic Pulse IDE.
**Usage:** `python scripts/startup_dashboard.py`

---

## 📊 Monitoring & Reporting

### `generate_report.py`
Analyzes `cap_swarm.db` and `cap_events.db` to produce a Markdown summary of "Market Vitality" and "Cognitive Telemetry".
**Usage:** `python scripts/generate_report.py`

### `update_apc_reports.py`
Automated job that periodically refreshes the system status reports in `docs/ss/`.

---

## 🔧 Maintenance

### `version_manager.py`
Increments the `VERSION` file and updates the dashboard fallback values. Supports Semantic Versioning (Major.Minor.Patch).

### `install_watchdog.sh`
Shell utility to install the necessary filesystem monitoring tools for the APC sandbox.

### `arm_worker.py`
A low-level worker that listens to the `task_queue` in the CLIDE database and dispatches events to the APC executor.
