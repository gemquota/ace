# 📖 GLOSSARY: SOVEREIGN COGNITIVE ARCHITECTURE

## Core Architecture

**CAP (Cognitive Architecture Platform):** A sovereign, multi-agent "Cognitive OS" built on event-sourced epistemology. At Phase 20, it is a self-evolving, economically regulated engineering intelligence.

**APC-RUNTIME:** The "Actuator" layer (Deterministic Execution). It executes commands in sandboxed environments, capturing filesystem side-effects as cryptographic hashes.

**PIE (Praxis Inference Engine):** The "Perception" layer (Causal Analysis). Ingests event traces to build multi-dimensional graphs (Temporal, Causal, Entity) and detect anomalies.

**CLIDE (Intent Compiler):** The "Will" layer (Goal Resolution). Compiles natural language or autonomous goals into structured Intent DAGs.

**Sovereign Engine:** The "Agency" layer (Autonomous Goal Generation). Monitors system health and generates independent goals to maintain stability or optimize architecture.

**Meta-Cognition Layer:** The "Self-Aware" layer (Architectural Evolution). Evaluates subsystem performance and conducts experiments to mutate the system's own configuration.

---

## Economic & Swarm Terminology

**Compute Credit (CR):** The internal currency of the CAP swarm. Used to "buy" execution time. Prevents resource exhaustion and enforces efficiency.

**Darwinian Pruning:** The process of archiving and removing low-performing or bankrupt agents from the swarm to optimize resource allocation.

**Genesis Bailout:** An emergency credit injection triggered when the entire agent population collapses, ensuring system continuity.

**Negotiation Session:** A multi-turn auction where agents bid on tasks based on their historical success confidence and proposed cost.

**Swarm Ledger:** The immutable record of all credit transactions and agent task assignments.

---

## Epistemic & Temporal Concepts

**Causal Parent:** The unique ID of the event that directly triggered the current event, forming the "Lineage" of a thought or action.

**Genesis Hash:** A SHA-256 identity anchor generated at system birth. Stored in `.env` and `cap_events.db` to prevent identity spoofing.

**Lamport Logical Clock:** A monotonic counter used for total ordering of events in a distributed multi-agent environment.

**Temporal Horizon:** A rolling 4-hour window that bounds a trace. Traces exceeding this window are halted or rolled back to ensure stability.

**Trace:** A continuous, causally-linked sequence of events representing a single "session" of work or thought.

---

## Technical Primitives

**Action Node:** An atomic unit of a plan, containing a command, its dependencies, and its importance.

**Deterministic State Capture:** The process of generating a `pre_state_hash` and `post_state_hash` to prove the exact filesystem changes caused by a command.

**Intent DAG:** A Directed Acyclic Graph of Action Nodes. The formal output of the CLIDE compiler.

**Side-Effect Hash:** A digest ($H(\text{pre} + \text{post})$) that definitively identifies the physical impact of an execution.

**Substrate Migration:** The process of transparently moving execution from the local Android host to a remote server based on hardware metrics (CPU/Thermal).

---

## Documentation Reasoning Trace
-   **Observed**: Synthesis of all terms used in the Phase 16-20 implementation and the 19 documentation files.
-   **Confidence Level**: 100%.
