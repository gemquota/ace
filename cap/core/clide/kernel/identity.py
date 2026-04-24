import os
import time
import hashlib
import sqlite3
from clide.storage import db

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

def generate_genesis_hash(trace_id: str) -> str:
    """Generate a unique Genesis Hash anchored to the first trace."""
    seed = f"clide_genesis_{trace_id}_{time.time()}".encode('utf-8')
    return hashlib.sha256(seed).hexdigest()

def init_genesis(trace_id: str):
    """Initialize Genesis Hash if not present, storing it in .env and DB."""
    # Check DB
    db_hash = db.get_genesis_hash()
    
    # Check .env
    env_hash = None
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                if line.startswith("CAP_GENESIS_HASH="):
                    env_hash = line.strip().split("=")[1]
                    break
    
    if not db_hash and not env_hash:
        new_hash = generate_genesis_hash(trace_id)
        db.set_genesis_hash(new_hash)
        with open(ENV_PATH, "a") as f:
            f.write(f"\nCAP_GENESIS_HASH={new_hash}\n")
        print(f"[*] GENESIS HASH CREATED: {new_hash[:8]}...")
        return new_hash
    elif db_hash and env_hash:
        if db_hash != env_hash:
            raise RuntimeError("CRITICAL IDENTITY MISMATCH: DB Genesis Hash != .env Genesis Hash")
        return db_hash
    else:
        # Resolve partial initialization
        resolved_hash = db_hash or env_hash
        if not db_hash:
            db.set_genesis_hash(resolved_hash)
        if not env_hash:
            with open(ENV_PATH, "a") as f:
                f.write(f"\nCAP_GENESIS_HASH={resolved_hash}\n")
        return resolved_hash

def verify_genesis() -> bool:
    """Verify that the DB and .env Genesis hashes match."""
    db_hash = db.get_genesis_hash()
    if not db_hash:
        return False
    
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                if line.startswith("CAP_GENESIS_HASH="):
                    env_hash = line.strip().split("=")[1]
                    return db_hash == env_hash
    return False
