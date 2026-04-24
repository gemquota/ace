# core_clide_kernel_events.py

## 🧩 Metadata
- **Module:** `CLIDE`
- **Subsystem:** `Kernel`
- **Function:** Event sourcing and storage interface for cognitive events.
- **Source Path:** `core/clide/kernel/events.py`

## 📝 Description
`core_clide_kernel_events.py` defines the core `Event` data structure and its associated logic for serialization, integrity verification, and causal consistency. It is the primary vehicle for recording all significant cognitive and operational activities within the CAP system.

## 🛠️ Technical Reality

### 1. The `Event` Class
The central data structure for the system's event-sourced architecture.
-   **Fields:**
    -   `event_id`: A unique UUID string identifying the event.
    -   `trace_id`: The ID of the execution trace (goal) this event belongs to.
    -   `node_id`: The ID of the node (e.g., Termux, Windows) where the event was generated.
    -   `timestamp`: Real-world Unix timestamp.
    -   `logical_clock`: Lamport clock timestamp for causal ordering.
    -   `layer`: The subsystem layer (CLIDE, APC, PIE, etc.) that generated the event.
    -   `event_type`: A specific type from the `EventType` enumeration (e.g., GOAL_GENERATED, EXEC_COMPLETE).
    -   `payload`: A dictionary containing the actual event data (e.g., commands, results, inferences).
    -   `causal_parent`: The ID of the event that directly preceded and caused this one.
    -   `state_hash`: A SHA-256 hash for verifying the integrity of the event and its causal context.

### 2. Integrity Verification
-   **`_calculate_hash()`:** Generates a deterministic SHA-256 hash of the event's core fields (excluding the hash itself). This provides a mechanism for verifying that an event has not been tampered with and maintains a consistent causal link to its parent.

### 3. Serialization Interface
Provides methods for converting events to and from dictionary formats suitable for persistence (SQLite) or network transmission (JSON).
-   **`to_dict()`:** Converts the event instance into a dictionary, serializing the payload into a JSON string.
-   **`from_dict()`:** Reconstructs an `Event` instance from a dictionary representation.

### 4. Node Identification
-   **`get_node_id()`:** Retrieves the current node's identifier from the `CAP_NODE_ID` environment variable, defaulting to "default_node" if not set. This is crucial for tracking events across a distributed mesh.

## 🔗 Dependencies
-   **Python standard library:** `uuid`, `json`, `hashlib`, `os`.
-   **CLIDE Types:** Imports `Layer` and `EventType` enumerations.
-   **CLIDE Kernel Clock:** Typically used to generate the `logical_clock` value before event creation.
-   **PIE Engine:** Consumes `Event` streams for causal graph reconstruction.
