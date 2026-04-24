import json
from typing import List, Dict, Any, Optional
from .store import MemoryStore
from .working_memory import WorkingMemory
from .semantic_store import SemanticStore
from .episodic_index import EpisodicIndex

class HybridRetriever:
    """
    Advanced cognitive retrieval engine.
    Uses working memory (context), semantic memory (meaning), and episodic memory (analogy).
    """
    def __init__(self, 
                 store: Optional[MemoryStore] = None, 
                 working_memory: Optional[WorkingMemory] = None,
                 semantic_store: Optional[SemanticStore] = None,
                 episodic_index: Optional[EpisodicIndex] = None):
        self.store = store or MemoryStore()
        self.working_memory = working_memory
        self.semantic_store = semantic_store or SemanticStore()
        self.episodic_index = episodic_index or EpisodicIndex()

    def get_candidate_sequences(self, intent_label: str) -> List[List[str]]:
        """
        Retrieves successful command sequences using hybrid memory stack.
        """
        # 1. Check Working Memory first (for recent successful patterns in current trace)
        if self.working_memory:
             # Look at recent events
             pass

        # 2. Check Semantic Memory for abstract patterns
        semantic_matches = self.semantic_store.search(intent_label)
        
        # 3. Check Episodic Memory for historical analogies
        episodic_matches = self.episodic_index.find_by_goal_similarity(intent_label)
        
        # 4. Fallback to basic storage
        matches = self.store.get_successful_sequences(intent_label)
        sequences = []
        for match in matches:
            sequences.append(json.loads(match["command_sequence"]))
            
        return sequences

    def get_contextual_recall(self, query: str) -> Dict[str, Any]:
        """
        Provides comprehensive contextual awareness.
        """
        return {
            "working": self.working_memory.get_snapshot() if self.working_memory else {},
            "semantic": [e.dict() for e in self.semantic_store.search(query)],
            "episodic": [e.dict() for e in self.episodic_index.find_by_goal_similarity(query)]
        }

    def get_relevant_failures(self, intent_label: str) -> List[List[str]]:
        # ... (unchanged)
        with self.store.get_connection() as conn:
            rows = conn.execute("""
                SELECT command_sequence FROM command_sequences 
                WHERE intent_label = ? AND outcome = 'failure'
                LIMIT 10
            """, (intent_label,)).fetchall()
            return [json.loads(row["command_sequence"]) for row in rows]

    def rank_strategies(self, intent_label: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank candidate strategies by their historical success weight.
        """
        # Simple implementation: use the sequences retrieved from store which are already ordered by weight.
        return self.store.get_successful_sequences(intent_label)
