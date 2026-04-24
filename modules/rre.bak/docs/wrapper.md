# RRE Wrapper & Orchestration Layer

The RRE Wrapper is the primary orchestration layer that binds the components of the Recursive Reinforcement Engine together. It operates as the central nervous system connecting the Conversational Layer (L1) and the System Integrity Layer (L2) with external interfaces.

## 1. Core Responsibilities
- **Input Routing**: Intercepts user inputs and evaluates whether they should be processed by L1 (for dialogue generation) or L2 (for constraint extraction and ambiguity scoring).
- **Initialization Management**: Handles the startup sequence, parsing commands like "AUTO" or specific variable assignments (e.g., `U=3, M=2`) into a structured session configuration.
- **Artifact Factory**: Manages the final synthesis phase. When Z rounds are completed, it triggers the generation of the `intent.md`, Traceability Matrix, and Mermaid diagrams based on the accumulated State Snapshot.

## 2. API & Integration Surface
- **Session Management**: Supports multiple concurrent chat sessions with unique IDs.
- **Multi-Agent Coordination**: Allows routing prompts between multiple AI instances (e.g., standard Gemini, specialized coding agents, or adversarial "Red Team" instances for U=4).
- **Historical Persistence**: Archives all State Snapshots and Rolling Summaries to durable storage (e.g., SQLite or flat JSON files), enabling sessions to be paused and resumed.

## 3. Cognitive Dimension Adjustments
The wrapper continuously monitors the `Ambiguity Vector`. If ambiguity remains high across multiple turns, the wrapper automatically adjusts the cognitive dimensions:
- Increases `X` (Open Questions) to force more exploration.
- Elevates `Depth` from `STANDARD` to `DEEP` if contradictions are detected.