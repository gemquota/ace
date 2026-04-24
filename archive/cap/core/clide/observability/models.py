import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class CognitiveEventType(Enum):
    DECISION = "DECISION"
    INFERENCE = "INFERENCE"
    ACTION = "ACTION"
    ERROR = "ERROR"
    SYSTEM = "SYSTEM"
    ECONOMIC = "ECONOMIC"

class CognitiveEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    type: CognitiveEventType
    agent_id: str
    trace_id: str
    inputs: List[Any] = Field(default_factory=list)
    outputs: List[Any] = Field(default_factory=list)
    confidence: float = 1.0
    parent_event_ids: List[str] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)

class RelationshipType(Enum):
    CAUSED = "CAUSED"
    INFLUENCED = "INFLUENCED"
    TRIGGERED = "TRIGGERED"
    REFINES = "REFINES"

class CausalEdge(BaseModel):
    from_event: str
    to_event: str
    relationship: RelationshipType
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentStatus(Enum):
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"

class AgentState(BaseModel):
    agent_id: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    score: float = 1.0
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    lineage: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)

class TransactionType(Enum):
    TASK_EXECUTION = "TASK_EXECUTION"
    RESOURCE_RENTAL = "RESOURCE_RENTAL"
    INCENTIVE = "INCENTIVE"
    PENALTY = "PENALTY"

class EconomicTransaction(BaseModel):
    tx_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    value: float
    reason: TransactionType
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
