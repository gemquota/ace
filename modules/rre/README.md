# 🖥️ RRE: Recursive Reinforcement Engine (Web Dashboard)

RRE is the high-fidelity web dashboard and orchestration engine for the **Recursive Refinement Protocol (RRP)**. It provides a multi-agent environment to visualize and execute complex architectural design sessions.

## 🚀 Overview

The **Recursive Reinforcement Engine (RRE)** serves as the graphical and server-side component for RRP sessions. While the protocol (RRP) defines the logic of refinement, RRE provides the "Hardened Core" to run these sessions with persistent state, multiple specialized agents, and a real-time Mermaid-enabled interface.

### 🧠 Dual-Layer Architecture

1.  **Conversational Layer (Interface Brain)**: Manages the user experience, pacing, and the rolling project summary.
2.  **System Integrity Layer (Core Brain)**: Silently tracks ambiguity vectors, locks immutable constraints, and injects failure scenarios to stress-test the design.

## 🛠 Features

-   **Variable-Driven Cognition**:
    -   `U` (Use Case): Pivot between Ideation, Convergence, and Stress Testing.
    -   `M` (Execution Mode): Choose between Flow, Batch, or Pulse pacing.
    -   `X/Y/Z`: Fine-tune the question budget and refinement rounds.
-   **Ambiguity Vectoring**: Multi-dimensional tracking of uncertainty across Requirements, Data Models, Edge Cases, and Determinism.
-   **Constraint Locking**: Irreversible storage of technical commitments.
-   **Dual-Interface**:
    -   **CLI Skill**: Integrated directly into Gemini CLI via `activate_skill ace-rrp`.
    -   **Web Dashboard**: A real-time, multi-agent interactive environment.

## 📦 Installation

RRE is a core architectural component. To initialize the dashboard and link the CLI tool:

```bash
./setup.sh
```

This script will:
1.  Link the `ace-rrp` CLI tool to your `~/bin`.
2.  Install required Python dependencies (`fastapi`, `uvicorn`, etc.).
3.  Initialize local data directories for session persistence.

## ⌨️ Usage

### Within Gemini CLI
Activate the expert refinement skill:
```text
activate_skill ace-rrp
```

### Standalone CLI Tool
Launch the web dashboard:
```bash
ace-rrp server --port 8000
```
Run a stateless query:
```bash
ace-rrp query "Architect a micro-service for high-frequency trading"
```

## 📉 Cognitive Dimensions (The Matrix)

| Variable | Mode | Focus |
| :--- | :--- | :--- |
| **U=1** | Alignment | General Clarity |
| **U=2** | Ideation | Divergent Brainstorming |
| **U=3** | Convergence | Hard Technical Commitments |
| **U=4** | Stress Test | Red Teaming & Risk |
| **U=5** | Data Mapping | Relationships & Schemas |
| **U=6** | Determinism | Edge Cases & Logic Gates |

## 🏗 Directory Structure

-   `app/`: FastAPI backend and React-based static frontend.
-   `docs/`: Core architectural specs and cognitive dimensions.
-   `archive/`: Legacy RRP logic and prototype scripts.
-   `.gemini/skills/ace-rrp/`: The Gemini CLI skill definition and state persistence.

## 📜 License
Internal Development - Proprietary Cognitive Architecture.
