import multiprocessing
import sys
import traceback
import subprocess
import time
import os
import uuid
from typing import Dict, Any, Optional

def _run_python_target(script_path: str, result_dict: Dict[str, Any]):
    """Target function for multiprocessing python execution."""
    import io
    import contextlib
    stdout = io.StringIO()
    stderr = io.StringIO()
    
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            with open(script_path, "r") as f:
                code = f.read()
            exec(code, {"__name__": "__main__"})
            result_dict["exit_code"] = 0
        except Exception:
            stderr.write(traceback.format_exc())
            result_dict["exit_code"] = 1
            
    result_dict["stdout"] = stdout.getvalue()
    result_dict["stderr"] = stderr.getvalue()

def execute_python_script(script_path: str, timeout_seconds: int = 10) -> Dict[str, Any]:
    """Execute a python script directly via multiprocessing with a timeout."""
    manager = multiprocessing.Manager()
    result_dict = manager.dict()
    result_dict["stdout"] = ""
    result_dict["stderr"] = ""
    result_dict["exit_code"] = -1
    
    start_time = time.time()
    p = multiprocessing.Process(target=_run_python_target, args=(script_path, result_dict))
    p.start()
    p.join(timeout_seconds)
    
    timeout_flag = False
    if p.is_alive():
        p.terminate()
        p.join()
        result_dict["stderr"] += f"\nExecution timed out after {timeout_seconds} seconds."
        result_dict["exit_code"] = 124
        timeout_flag = True
        
    duration_ms = int((time.time() - start_time) * 1000)
    
    return {
        "stdout": result_dict["stdout"],
        "stderr": result_dict["stderr"],
        "exit_code": result_dict["exit_code"],
        "timeout_flag": timeout_flag,
        "duration_ms": duration_ms
    }

from apc.hasher import calculate_input_hash, calculate_output_hash, hash_directory_state, calculate_sha256
from apc.sandbox import validate_command, prepare_sandbox, run_in_sandbox, cleanup_sandbox
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType

class ExecutionResult:
    def __init__(self, stdout: str, stderr: str, exit_code: int, duration_ms: int):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration_ms = duration_ms

def execute_command(
    trace_id: str,
    command: str,
    causal_parent: str,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
    persist_sandbox: bool = False
) -> Dict[str, Any]:
    env = env or os.environ.copy()
    cwd = cwd or os.getcwd()
    exec_id = str(uuid.uuid4())

    # 1. Pre-Execution Validation
    is_valid, error_msg = validate_command(command)
    
    # 2. Prepare Sandbox (if valid)
    sandbox_path = prepare_sandbox(trace_id, exec_id) if is_valid else "n/a"
    
    # 3. Pre-Execution Capture (using sandbox path for pre_state_hash)
    # We hash the empty sandbox or the current cwd if it's not sandboxed?
    # The requirement says "Set this as cwd for execution"
    # "Ensure all file operations occur within this directory"
    # So we should probably hash the sandbox directory.
    pre_state_hash = hash_directory_state(sandbox_path) if is_valid else "n/a"
    input_hash = calculate_input_hash(command, env, sandbox_path)
    
    # 4. Emit EXEC_SPAWN
    spawn_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.APC,
        event_type=EventType.EXEC_SPAWN,
        payload={
            "command": command,
            "cwd": sandbox_path,
            "input_hash": input_hash,
            "pre_state_hash": pre_state_hash,
            "sandbox_path": sandbox_path,
            "validated": is_valid
        },
        causal_parent=causal_parent
    )
    
    if not is_valid:
        stdout = ""
        stderr = f"VALIDATION_FAILED: {error_msg}"
        exit_code = -1
        duration_ms = 0
        timeout_flag = False
        truncated_output_flag = False
    else:
        # 5. Execution in Sandbox
        result = run_in_sandbox(command, sandbox_path, env=env)
        stdout = result["stdout"]
        stderr = result["stderr"]
        exit_code = result["exit_code"]
        duration_ms = result["duration_ms"]
        timeout_flag = result["timeout_flag"]
        truncated_output_flag = result["truncated_output_flag"]
    
    # 6. Post-Execution Capture
    post_state_hash = hash_directory_state(sandbox_path) if is_valid else "n/a"
    output_hash = calculate_output_hash(stdout, stderr, exit_code)
    side_effect_hash = calculate_sha256(pre_state_hash + post_state_hash) if is_valid else "n/a"
    
    # 7. Emit EXEC_COMPLETE
    complete_id = syscalls.cap_event_commit(
        trace_id=trace_id,
        layer=Layer.APC,
        event_type=EventType.EXEC_COMPLETE,
        payload={
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "duration_ms": duration_ms,
            "output_hash": output_hash,
            "side_effect_hash": side_effect_hash,
            "post_state_hash": post_state_hash,
            "timeout_flag": timeout_flag,
            "truncated_output_flag": truncated_output_flag
        },
        causal_parent=spawn_id
    )
    
    # 8. Cleanup
    if is_valid and not persist_sandbox:
        cleanup_sandbox(sandbox_path)
    
    return {
        "spawn_id": spawn_id,
        "complete_id": complete_id,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "timeout_flag": timeout_flag
    }
