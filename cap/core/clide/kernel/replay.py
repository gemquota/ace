import os
import json
import tempfile
import subprocess
from typing import List, Dict, Any
from dataclasses import dataclass
from clide.storage import db
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from apc.hasher import calculate_input_hash, calculate_output_hash, hash_directory_state, calculate_sha256

@dataclass
class Mismatch:
    event_id: str
    expected_hash: str
    actual_hash: str

@dataclass
class ReplayResult:
    trace_id: str
    status: str
    mismatches: List[Mismatch]

def cap_trace_replay(trace_id: str) -> ReplayResult:
    events = db.get_events_by_trace(trace_id)
    mismatches = []
    
    with tempfile.TemporaryDirectory() as sandbox_dir:
        for event in events:
            if event["event_type"] == EventType.EXEC_SPAWN.value:
                spawn = event
                # Find matching complete
                complete = None
                for e in events:
                    if e["causal_parent"] == spawn["event_id"] and e["event_type"] == EventType.EXEC_COMPLETE.value:
                        complete = e
                        break
                
                if not complete:
                    continue
                
                spawn_payload = json.loads(spawn["payload"]) if isinstance(spawn["payload"], str) else spawn["payload"]
                complete_payload = json.loads(complete["payload"]) if isinstance(complete["payload"], str) else complete["payload"]
                
                command = spawn_payload["command"]
                
                # Execute in sandbox
                env = os.environ.copy()
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=sandbox_dir
                )
                stdout, stderr = process.communicate()
                exit_code = process.returncode
                
                # Recompute output hash
                actual_output_hash = calculate_output_hash(stdout, stderr, exit_code)
                expected_output_hash = complete_payload["output_hash"]
                
                if actual_output_hash != expected_output_hash:
                    mismatches.append(Mismatch(
                        event_id=complete["event_id"],
                        expected_hash=expected_output_hash,
                        actual_hash=actual_output_hash
                    ))

    status = "PASS" if not mismatches else "FAIL"
    return ReplayResult(trace_id=trace_id, status=status, mismatches=mismatches)

def cap_rollback(trace_id: str, to_event_id: str):
    syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.CAP,
        event_type=EventType.ROLLBACK,
        payload={"target_event_id": to_event_id},
        causal_parent=None
    )
    return True
