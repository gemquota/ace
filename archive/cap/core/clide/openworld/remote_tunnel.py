import os
import json
import sqlite3
import threading
import time
import subprocess
from typing import Dict, Any, Optional

# Stub for paramiko to avoid dependency error if not installed
try:
    import paramiko
except ImportError:
    paramiko = None

REMOTE_NODE_IP = os.getenv("CAP_REMOTE_IP", "192.168.1.100")
REMOTE_USER = os.getenv("CAP_REMOTE_USER", "user")
REMOTE_KEY = os.getenv("CAP_REMOTE_KEY", "~/.ssh/id_rsa")

class RemoteCache:
    """Local SQLite WAL caching mechanism for the remote node to handle network drops."""
    def __init__(self, cache_path=None):
        if cache_path is None:
            # Use a writeable path in the project dir for Android/Termux
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cache_path = os.path.join(base_dir, "clide_remote_cache.db")
        self.cache_path = cache_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.cache_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS remote_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def cache_event(self, event_payload: Dict[str, Any]):
        with self._get_conn() as conn:
            conn.execute("INSERT INTO remote_events (payload) VALUES (?)", (json.dumps(event_payload),))
            conn.commit()

    def get_unsynced(self):
        with self._get_conn() as conn:
            rows = conn.execute("SELECT id, payload FROM remote_events WHERE synced = 0").fetchall()
            return [{"id": r[0], "payload": json.loads(r[1])} for r in rows]

    def mark_synced(self, event_ids):
        with self._get_conn() as conn:
            placeholders = ",".join("?" * len(event_ids))
            conn.execute(f"UPDATE remote_events SET synced = 1 WHERE id IN ({placeholders})", tuple(event_ids))
            conn.commit()

class RemoteTunnel:
    def __init__(self):
        self.cache = RemoteCache()
        self.sync_thread = threading.Thread(target=self._async_flush, daemon=True)
        self.sync_thread.start()
        
    def _async_flush(self):
        """Asynchronous cache-flushing back to the master Android DB."""
        from clide.storage import db # Master DB
        while True:
            unsynced = self.cache.get_unsynced()
            if unsynced:
                synced_ids = []
                for item in unsynced:
                    try:
                        # Assuming master DB is reachable and available
                        db.commit_event(item["payload"])
                        synced_ids.append(item["id"])
                    except Exception as e:
                        print(f"[!] REMOTE SYNC ERROR: {e}")
                        break # Stop on first failure to preserve order
                if synced_ids:
                    self.cache.mark_synced(synced_ids)
            time.sleep(5)

    def execute_remote(self, command: str) -> Dict[str, Any]:
        """Execute a payload via paramiko SSH connection."""
        print(f"[*] TUNNEL: Executing remotely on {REMOTE_NODE_IP}: {command}")
        
        if not paramiko:
            print("[!] paramiko not installed. Simulating remote execution...")
            # Simulate remote execution locally for testing if paramiko is missing
            res = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.returncode
            }

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(REMOTE_NODE_IP, username=REMOTE_USER, key_filename=os.path.expanduser(REMOTE_KEY), timeout=10)
            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            
            return {
                "stdout": out,
                "stderr": err,
                "exit_code": exit_code
            }
        except Exception as e:
            print(f"[!] SSH Tunnel Error: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
        finally:
            client.close()
