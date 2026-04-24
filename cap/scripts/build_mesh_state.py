import os
import json
import sqlite3
import redis
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CAP_DIR = BASE_DIR / ".cap"
MANIFEST_PATH = CAP_DIR / "operator_manifest.json"

def init_directories():
    print("[*] Initializing Directory Topography...")
    for d in ["data", "logs/traces", "logs/backups"]:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

def init_databases():
    print("[*] Building Master Event Ledger (SQLite)...")
    db_path = DATA_DIR / "cap_events.db"
    conn = sqlite3.connect(db_path)
    # Re-run forensic schemas if necessary
    with open(BASE_DIR / "core/clide/storage/schema.sql", 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def init_redis():
    print("[*] Initializing Swarm State Broker (Redis)...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("[+] Redis Online.")
    except Exception as e:
        print(f"[!] Warning: Redis not detected. Swarm Grid will require 'redis-server' background daemon.")

def sync_manifest():
    print("[*] Synchronizing Operator Manifest...")
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
        manifest["last_sync"] = "Thu Apr 9 2026"
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    init_directories()
    init_databases()
    init_redis()
    sync_manifest()
    print("\n[+] CAP V3.1.0 SWARM_GRID BOOTSTRAP COMPLETE.")
