import sqlite3
import json

class TelemetrySubstrate:
    def __init__(self, broadcast_queue=None):
        self.db = sqlite3.connect("metrics.db", check_same_thread=False)
        self.broadcast_queue = broadcast_queue
        self._init_db()

    def _init_db(self):
        c = self.db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS telemetry (tick INT, agent_id TEXT, role TEXT, score REAL, entropy REAL)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_tick ON telemetry(tick)''')
        c.execute('''CREATE TABLE IF NOT EXISTS quarantine (agent_id TEXT, tick INT, lost_data TEXT)''')
        self.db.commit()

    def record(self, tick, payload):
        c = self.db.cursor()
        c.execute("INSERT INTO telemetry VALUES (?, ?, ?, ?, ?)", 
                  (tick, payload.agent_id, payload.current_role, payload.priority_score, payload.entropy_index))
        self.db.commit()
        
        if self.broadcast_queue is not None:
             event = {
                 "type": "telemetry",
                 "data": {
                     "tick": tick,
                     "agent_id": payload.agent_id,
                     "role": payload.current_role,
                     "score": payload.priority_score,
                     "entropy": payload.entropy_index
                 }
             }
             self.broadcast_queue.put_nowait(json.dumps(event))

    def quarantine(self, tick, agent_id, lost_data):
        c = self.db.cursor()
        c.execute("INSERT INTO quarantine VALUES (?, ?, ?)", 
                  (agent_id, tick, json.dumps(lost_data)))
        self.db.commit()
