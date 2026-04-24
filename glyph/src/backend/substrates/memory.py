import chromadb
from sentence_transformers import SentenceTransformer

class MemorySubstrate:
    def __init__(self, seed):
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection(name=f"swarm_{seed}")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def query(self, text, coherence_threshold=0.3):
        emb = self.encoder.encode([text])[0].tolist()
        results = self.collection.query(query_embeddings=[emb], n_results=1, where={"coherence": {"$gte": coherence_threshold}})
        if results['documents'] and results['documents'][0]:
            return results['documents'][0][0]
        return None

    def store(self, text, agent_id, tick, coherence):
        emb = self.encoder.encode([text])[0].tolist()
        doc_id = f"mem_{agent_id}_{tick}"
        self.collection.add(ids=[doc_id], embeddings=[emb], documents=[text], metadatas=[{"coherence": coherence}])
