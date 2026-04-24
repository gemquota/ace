DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS traces;
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS causal_index;
DROP TABLE IF EXISTS message_bus;
DROP TABLE IF EXISTS task_queue;

CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    logical_clock INTEGER NOT NULL,
    layer TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT, -- JSON content
    causal_parent TEXT,
    state_hash TEXT NOT NULL,
    FOREIGN KEY (trace_id) REFERENCES traces(trace_id)
);

CREATE TABLE IF NOT EXISTS nodes (
    node_id TEXT PRIMARY KEY,
    last_seen INTEGER NOT NULL,
    active_tasks INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS task_queue (
    task_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    causal_parent TEXT,
    action_payload TEXT NOT NULL, -- JSON ActionNode
    priority REAL DEFAULT 5.0,
    status TEXT DEFAULT 'PENDING', -- PENDING, CLAIMED, SUCCESS, FAILED
    node_id TEXT, -- The worker that claimed it
    lease_expiry INTEGER,
    created_at INTEGER NOT NULL,
    completed_at INTEGER,
    FOREIGN KEY (trace_id) REFERENCES traces(trace_id)
);

CREATE TABLE IF NOT EXISTS causal_index (
    child_event_id TEXT,
    parent_event_id TEXT,
    PRIMARY KEY (child_event_id, parent_event_id),
    FOREIGN KEY (child_event_id) REFERENCES events(event_id),
    FOREIGN KEY (parent_event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS message_bus (
    msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS system_identity (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    genesis_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trace_id ON events(trace_id);
CREATE INDEX IF NOT EXISTS idx_layer ON events(layer);
CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_logical_clock ON events(logical_clock);
