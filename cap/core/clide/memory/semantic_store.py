import uuid
import time
import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SemanticEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    embedding: List[float] = Field(default_factory=list)
    text: str
    source: str # e.g. episode_id or 'manual_injection'
    confidence: float = 1.0
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SemanticStore:
    """
    Stores abstract knowledge, facts, and patterns.
    Enables semantic reasoning and long-term intelligence.
    """
    def __init__(self, db_path: str = "data/semantic_memory.json"):
        self.db_path = db_path
        self.entries: Dict[str, SemanticEntry] = {}
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.db_path):
             try:
                 with open(self.db_path, "r") as f:
                     data = json.load(f)
                     self.entries = {eid: SemanticEntry.parse_obj(e) for eid, e in data.items()}
             except: pass

    def save_store(self):
        with open(self.db_path, "w") as f:
            json.dump({eid: e.dict() for eid, e in self.entries.items()}, f, indent=2)

    def add_entry(self, entry: SemanticEntry):
        self.entries[entry.id] = entry
        self.save_store()

    def search(self, query: str, limit: int = 5) -> List[SemanticEntry]:
        """
        Placeholder for semantic similarity search.
        Currently uses simple keyword matching.
        """
        results = []
        for e in self.entries.values():
            if query.lower() in e.text.lower():
                results.append(e)
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:limit]

    def cluster_patterns(self) -> Dict[str, List[str]]:
        """
        Placeholder for concept clustering.
        """
        return {}
