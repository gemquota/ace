import hashlib
import json
import os
from typing import Dict, Any

def calculate_sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def hash_directory_state(path: str) -> str:
    """
    Heuristic: hash filenames + sizes + mtimes for speed.
    """
    state = []
    try:
        for root, dirs, files in os.walk(path):
            # Sort to ensure determinism
            dirs.sort()
            files.sort()
            for name in files:
                fpath = os.path.join(root, name)
                try:
                    stat = os.stat(fpath)
                    state.append(f"{fpath}:{stat.st_size}:{stat.st_mtime}")
                except OSError:
                    continue
    except Exception:
        pass
    
    return calculate_sha256("\n".join(state))

def calculate_input_hash(command: str, env: Dict[str, str], cwd: str) -> str:
    serialized_env = json.dumps(env, sort_keys=True)
    return calculate_sha256(command + serialized_env + cwd)

def calculate_output_hash(stdout: str, stderr: str, exit_code: int) -> str:
    return calculate_sha256(stdout + stderr + str(exit_code))
