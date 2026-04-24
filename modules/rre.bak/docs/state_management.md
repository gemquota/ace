# RRE State Management

RRE guarantees continuity across massive, complex design sessions using a structured state object.

## 1. The State Anchor
A JSON-serializable object that precedes every internal evaluation:
```json
{
  "U": 3, "M": 1, "round": 2, "max_rounds": 5,
  "pending_open_qs": 2, "pending_mcqs": 4
}
```

## 2. Rolling Project Summary
A continuously updated markdown narrative. L1 rewrites this summary every turn to include new decisions, replacing outdated assumptions. It serves as the master context payload to prevent token drift.

## 3. Ambiguity Vector
A multi-dimensional scoring system (0.0 to 1.0) maintained by L2:
- `requirements_clarity`: How well the goal is defined.
- `data_model_definition`: Completeness of schemas and entities.
- `edge_case_coverage`: Percentage of identified edge cases with mitigations.
- `deterministic_behavior`: Confidence that all logic branches resolve cleanly.
*If the average vector falls below 0.8 at round Z, the system refuses to generate the final blueprint and adds a new round.*

## 4. State Snapshot
At the end of each round, L2 compresses the session into a `snapshot.json` containing:
- Confirmed Goals
- Immutable Constraints
- Decision Log (Why X was chosen over Y)
- Outstanding Risks