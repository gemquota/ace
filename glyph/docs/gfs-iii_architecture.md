# GFS-III Architecture Overview

**Status**: Active Production
**Version**: 3.0

## 1. The Substrate Model
The GFS-III engine has evolved past the monolithic bottleneck of v2. It now operates on a modular, 4-pillar Substrate architecture:

1. **Cognitive Substrate**: Handles LLM orchestration, tiered model routing (Flash vs Pro), and agent role-playing.
2. **Memory Substrate**: Manages Vector embeddings via ChromaDB and SentenceTransformers for semantic recall.
3. **Telemetry Substrate**: Handles SQLite-based metrics tracking (entropy, priority, tick count) for performance auditing.
4. **Topology Substrate**: Controls NetworkX graph state, garbage collection, and guarded mutations (pruning/adding nodes safely).

## 2. The Engine Dispatcher
The `Engine` class now acts purely as a dispatcher. During `step()`, it updates telemetry, handles garbage collection, and delegates glyph execution to the appropriate Substrate.

## 3. Legacy Documentation
All legacy GFS-II v1 and v2 technical reports, including the monolithic "recursion" blob, have been successfully decoupled and archived in `docs/archive/`.
