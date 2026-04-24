import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from clide.observability.aggregator import ObservabilityAggregator
from clide.observability.models import CognitiveEvent, CausalEdge
from clide.storage import db

class StreamProcessor:
    def __init__(self, aggregator: ObservabilityAggregator):
        self.aggregator = aggregator
        self.subscribers: List[Callable] = []
        self._last_rowid = 0

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    async def broadcast(self, message: Dict[str, Any]):
        for sub in self.subscribers:
            if asyncio.iscoroutinefunction(sub):
                await sub(message)
            else:
                sub(message)

    async def poll_and_process(self):
        """
        Polls the events table, normalizes events, and broadcasts them using ACE_EVENT_BUS headers.
        """
        import time
        while True:
            try:
                with db.get_connection() as conn:
                    # Need rowid for polling
                    rows = conn.execute("SELECT *, rowid FROM events WHERE rowid > ? ORDER BY rowid ASC", (self._last_rowid,)).fetchall()
                    for row in rows:
                        raw_event = dict(row)
                        self._last_rowid = raw_event["rowid"]
                        
                        cog_event = self.aggregator.normalize_raw_event(raw_event)
                        if cog_event:
                            # Enrich with causal edges
                            edges = self.aggregator.build_causal_edges(cog_event)
                            
                            # Construct ACE_EVENT_BUS Header
                            message = {
                                "trace_id": cog_event.trace_id,
                                "source": "CLIDE", # Polled from persistence
                                "type": "COGNITIVE_EVENT",
                                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                                "payload": {
                                    "event": cog_event.dict(),
                                    "edges": [e.dict() for e in edges]
                                }
                            }
                            await self.broadcast(message)
                            
                            # Also check for agent state changes
                            agent_state = self.aggregator.extract_agent_state(cog_event)
                            if agent_state:
                                await self.broadcast({
                                    "trace_id": cog_event.trace_id,
                                    "source": "CLIDE",
                                    "type": "AGENT_STATE",
                                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                                    "payload": {
                                        "state": agent_state.dict()
                                    }
                                })
            except Exception as e:
                # In a real system, use proper logging
                print(f"[StreamProcessor] Error polling: {e}")
            await asyncio.sleep(0.5)
