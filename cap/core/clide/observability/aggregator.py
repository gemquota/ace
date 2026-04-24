import json
from typing import List, Dict, Any, Optional
from clide.storage import db
from clide.observability.models import (
    CognitiveEvent, CognitiveEventType, CausalEdge, RelationshipType,
    AgentState, AgentStatus, EconomicTransaction, TransactionType
)
from clide.types.event_types import EventType, Layer

class ObservabilityAggregator:
    def __init__(self):
        self._processed_event_ids: set = set()

    def normalize_raw_event(self, raw_event: Dict[str, Any]) -> Optional[CognitiveEvent]:
        """
        Maps a raw event from cap_events.db to a CognitiveEvent.
        """
        event_id = raw_event["event_id"]
        trace_id = raw_event["trace_id"]
        event_type = raw_event["event_type"]
        layer = raw_event["layer"]
        payload = json.loads(raw_event["payload"]) if isinstance(raw_event["payload"], str) else raw_event["payload"]
        timestamp = raw_event["timestamp"]
        causal_parent = raw_event["causal_parent"]

        # Determine agent_id (heuristic: check payload or default to 'prime')
        agent_id = payload.get("agent_id") or "prime"

        # Map EventType to CognitiveEventType
        cog_type = CognitiveEventType.SYSTEM
        if event_type in [EventType.GOAL_GENERATED.value, EventType.STRATEGY_SWITCH.value, "DECISION"]:
            cog_type = CognitiveEventType.DECISION
        elif event_type in ["INFERENCE_COMPLETE", "CAUSAL_ANALYSIS"]:
            cog_type = CognitiveEventType.INFERENCE
        elif event_type in [EventType.EXEC_COMPLETE.value, "ACTION_START"]:
            cog_type = CognitiveEventType.ACTION
        elif "FAIL" in event_type or "ERROR" in event_type:
            cog_type = CognitiveEventType.ERROR
        elif "SPENT" in event_type or "EARNED" in event_type or "TRANSACTION" in event_type:
            cog_type = CognitiveEventType.ECONOMIC

        # Create CognitiveEvent
        cog_event = CognitiveEvent(
            id=event_id,
            timestamp=timestamp,
            type=cog_type,
            agent_id=agent_id,
            trace_id=trace_id,
            payload=payload,
            confidence=payload.get("confidence", 1.0),
            parent_event_ids=[causal_parent] if causal_parent else []
        )
        
        # Enrichment based on payload
        if cog_type == CognitiveEventType.ACTION:
            cog_event.inputs = [payload.get("command", "")]
            cog_event.outputs = [payload.get("stdout", ""), payload.get("stderr", "")]
        elif cog_type == CognitiveEventType.INFERENCE:
            cog_event.inputs = payload.get("relevant_traces", [])
            cog_event.outputs = [payload.get("conclusions", "")]

        return cog_event

    def build_causal_edges(self, cog_event: CognitiveEvent) -> List[CausalEdge]:
        edges = []
        for parent_id in cog_event.parent_event_ids:
            edges.append(CausalEdge(
                from_event=parent_id,
                to_event=cog_event.id,
                relationship=RelationshipType.CAUSED # Default
            ))
        return edges

    def extract_agent_state(self, cog_event: CognitiveEvent) -> Optional[AgentState]:
        # Heuristic: extract state if event contains it
        if cog_event.agent_id:
            return AgentState(
                agent_id=cog_event.agent_id,
                role="unknown", # Need better metadata
                status=AgentStatus.ACTIVE,
                timestamp=cog_event.timestamp
            )
        return None

    def extract_economic_transaction(self, raw_event: Dict[str, Any]) -> Optional[EconomicTransaction]:
        # This might need to look at cap_swarm.db instead of just raw_event
        payload = json.loads(raw_event["payload"]) if isinstance(raw_event["payload"], str) else raw_event["payload"]
        if "SPENT" in raw_event["event_type"] or "EARNED" in raw_event["event_type"]:
             return EconomicTransaction(
                 from_agent=payload.get("from_agent") or "prime",
                 to_agent=payload.get("to_agent") or "swarm",
                 value=payload.get("amount", 0.0),
                 reason=TransactionType.TASK_EXECUTION,
                 timestamp=raw_event["timestamp"]
             )
        return None
