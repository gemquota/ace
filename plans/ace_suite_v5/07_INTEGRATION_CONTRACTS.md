# 📡 ACE INTEGRATION CONTRACTS: THE TRIPLE-PACK SCHEMA // v0.1.0

## 1. The Triple-Pack Cognitive Particle
Every agent logic or system intent MUST be encapsulated in this schema:
```json
{
  "particle_id": "uuid-v4",
  "glyph_code": "⟐(...)⟳",
  "ast": { "type": "Program", "body": [] },
  "intent_dag": { "nodes": [], "edges": [] },
  "metadata": {
    "author": "human | machine",
    "pseudocode": "Human-readable explanation",
    "version": "1.0.0"
  }
}
```

## 2. Sync Protocol (ACE_SYNC_BUS)
Messages for the Local-First synchronization loop:
```json
{
  "sync_id": "uuid",
  "action": "SYNC_FRAGMENT | SYNC_KEYSTROKE | SYNC_RECONCILE",
  "target": "chats | snippets | contexts | graph",
  "payload": {},
  "timestamp": "ISO-8601"
}
```

## 3. APC Diff Artifacts
Schema for sandboxed execution reports:
```json
{
  "trace_id": "uuid",
  "exit_code": 0,
  "diff_summary": "3 files changed, 42 insertions(+)",
  "diff_patch": "raw patch string",
  "artifacts": [
    { "path": "data/artifacts/[uuid].patch", "type": "patch" }
  ]
}
```

## 4. PIE Introspection Reports
Schema for causal trace artifacts:
```json
{
  "report_id": "diag-uuid",
  "causal_score": 0.85,
  "inferred_failure_node": "glyph_node_id",
  "markdown_path": "reports/TRACE_[ID]_DIAG.md",
  "visual_overlay": {
    "type": "GHOST_SUBTREE | VIBRATION_PULSE",
    "affected_nodes": []
  }
}
```

---
*Verified by the RRP-forged ACE Sovereign Orchestrator.*
