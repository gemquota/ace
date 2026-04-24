import uuid
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Episode(BaseModel):
    episode_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    start_time: float
    end_time: Optional[float] = None
    goal: str
    events: List[str] = Field(default_factory=list) # List of event_ids
    outcome: str = "unknown" # success, failure, partial
    agents_involved: List[str] = Field(default_factory=list)
    key_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class EpisodicIndex:
    """
    Manages the collection of system episodes.
    Stores and retrieves historical experiences.
    """
    def __init__(self, db_path: str = "data/episodic_memory.json"):
        self.db_path = db_path
        self.episodes: Dict[str, Episode] = {}
        self._load_index()

    def _load_index(self):
        import os
        import json
        if os.path.exists(self.db_path):
             try:
                 with open(self.db_path, "r") as f:
                     data = json.load(f)
                     self.episodes = {eid: Episode.parse_obj(e) for eid, e in data.items()}
             except: pass

    def save_index(self):
        import json
        with open(self.db_path, "w") as f:
            json.dump({eid: e.dict() for eid, e in self.episodes.items()}, f, indent=2)

    def add_episode(self, episode: Episode):
        self.episodes[episode.episode_id] = episode
        self.save_index()

    def find_by_goal_similarity(self, goal_query: str) -> List[Episode]:
        # Simple string-matching for now, semantic in Semantic Memory layer
        results = []
        for e in self.episodes.values():
            if goal_query.lower() in e.goal.lower():
                results.append(e)
        return results

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        return self.episodes.get(episode_id)

    def list_successful_episodes(self) -> List[Episode]:
        return [e for e in self.episodes.values() if e.outcome == "success"]
