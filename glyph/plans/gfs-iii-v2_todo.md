# GFS-III v2: Distributed Substrates (TODO)

## Objectives
- [ ] **Redis Integration**: Move Telemetry and Memory states to Redis for multi-worker support.
- [ ] **Async Engine**: Refactor `Engine.step()` to use native `asyncio.gather` for parallel node propagation.
- [ ] **REST API Expansion**: Add endpoints for real-time graph modification (`POST /api/mutate`).
