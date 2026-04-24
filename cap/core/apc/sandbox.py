import os
import shutil
import shlex
import subprocess
import time
from typing import Dict, Any, List, Optional, Tuple

SANDBOX_BASE = os.path.expanduser("~/.cap_sandbox")
DEFAULT_TIMEOUT = 5
DEFAULT_MAX_OUTPUT_KB = 100

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "dd if=",
    "mkfs",
    "shutdown",
    "reboot",
    ":(){ :|:& };:" # Fork bomb
]

FORBIDDEN_PATHS = ["../", "/etc", "/system", "/proc", "/sys", "~"]

def validate_command(command: str) -> Tuple[bool, Optional[str]]:
    """
    Validates a command against dangerous patterns and path traversal.
    Returns (is_valid, error_message)
    """
    # 1. Denylist dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in command:
            return False, f"Dangerous command pattern detected: {pattern}"

    # 2. Filesystem Guard
    for forbidden in FORBIDDEN_PATHS:
        if forbidden in command:
            return False, f"Forbidden path or traversal detected: {forbidden}"

    return True, None

def prepare_sandbox(trace_id: str, exec_id: str) -> str:
    """
    Creates a unique sandbox directory for execution.
    """
    sandbox_path = os.path.join(SANDBOX_BASE, trace_id, exec_id)
    os.makedirs(sandbox_path, exist_ok=True)
    return sandbox_path

def cleanup_sandbox(sandbox_path: str):
    """
    Removes the sandbox directory.
    """
    if os.path.exists(sandbox_path):
        shutil.rmtree(sandbox_path)

def run_in_sandbox(
    command: str,
    sandbox_path: str,
    env: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    max_output_kb: int = DEFAULT_MAX_OUTPUT_KB
) -> Dict[str, Any]:
    """
    Executes a command within the specified sandbox directory with constraints.
    """
    args = shlex.split(command)
    
    start_time = time.time()
    timeout_flag = False
    truncated_output_flag = False
    
    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=sandbox_path
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            timeout_flag = True
            
        exit_code = process.returncode if not timeout_flag else -2
        
    except Exception as e:
        stdout = ""
        stderr = str(e)
        exit_code = -1
        
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Handle output truncation
    max_bytes = max_output_kb * 1024
    if len(stdout) > max_bytes:
        stdout = stdout[:max_bytes] + "\n[...TRUNCATED...]"
        truncated_output_flag = True
        
    if len(stderr) > max_bytes:
        stderr = stderr[:max_bytes] + "\n[...TRUNCATED...]"
        truncated_output_flag = True

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "timeout_flag": timeout_flag,
        "truncated_output_flag": truncated_output_flag
    }
