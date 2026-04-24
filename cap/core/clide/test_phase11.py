import os
import shutil
import time
from apc.executor import execute_command
from clide.kernel import syscalls
from clide.storage import db

def test_phase11_sandboxing():
    print("Initializing Phase 11 Test...")
    trace_id = syscalls.cap_trace_start()
    
    # 1. Test Command Validation (Dangerous Pattern)
    print("[*] Test 1: Dangerous Command Rejection")
    res = execute_command(trace_id, "rm -rf /", "root_parent")
    if "VALIDATION_FAILED" in res["stderr"] and res["exit_code"] == -1:
        print("  SUCCESS: Dangerous command blocked.")
    else:
        print(f"  FAILED: Command not blocked. Result: {res}")
        return False

    # 2. Test Filesystem Guard (Path Traversal)
    print("[*] Test 2: Path Traversal Rejection")
    res = execute_command(trace_id, "cat ../secrets.txt", "root_parent")
    if "VALIDATION_FAILED" in res["stderr"]:
        print("  SUCCESS: Path traversal blocked.")
    else:
        print(f"  FAILED: Path traversal not blocked. Result: {res}")
        return False

    # 3. Test Sandbox Isolation
    print("[*] Test 3: Sandbox Isolation")
    # Note: Since shell=False, we can't use 'touch file && ls'. 
    # We'll run them as separate execute_command calls in the SAME sandbox? 
    # Wait, execute_command creates a NEW sandbox for every call.
    # To test isolation, we check that files created in one don't exist in another, 
    # or that they don't exist in the host.
    
    # Create a file in sandbox
    res1 = execute_command(trace_id, "touch sandbox_file.txt", "root_parent", persist_sandbox=True)
    import json
    event = db.get_event(res1["spawn_id"])
    payload = json.loads(event["payload"])
    sandbox_path = payload["sandbox_path"]
    
    if os.path.exists(os.path.join(sandbox_path, "sandbox_file.txt")):
        print("  SUCCESS: File created in sandbox.")
    else:
        print("  FAILED: File not found in sandbox.")
        return False
        
    if not os.path.exists("sandbox_file.txt"):
        print("  SUCCESS: File not created in host.")
    else:
        print("  FAILED: File leaked to host!")
        shutil.rmtree(sandbox_path)
        os.remove("sandbox_file.txt")
        return False

    # 4. Test Timeout Handling
    print("[*] Test 4: Timeout Handling")
    # 'sleep 10' should timeout (default 5s)
    res_timeout = execute_command(trace_id, "sleep 10", "root_parent")
    if res_timeout["timeout_flag"] and res_timeout["exit_code"] == -2:
        print("  SUCCESS: Command timed out correctly.")
    else:
        print(f"  FAILED: Timeout failed. Result: {res_timeout}")
        return False

    # 5. Test Output Truncation
    print("[*] Test 5: Output Truncation")
    # Generate large output
    # Since we don't have shell redirections, we might need a script or a command that outputs a lot.
    # 'python3 -c "print('A'*200000)"'
    large_cmd = "python3 -c \"print('A'*200000)\""
    res_trunc = execute_command(trace_id, large_cmd, "root_parent")
    
    event_complete = db.get_event(res_trunc["complete_id"])
    payload_complete = json.loads(event_complete["payload"])
    if payload_complete["truncated_output_flag"]:
        print("  SUCCESS: Output truncated correctly.")
    else:
        print("  FAILED: Output not truncated.")
        return False

    # Cleanup
    shutil.rmtree(os.path.dirname(sandbox_path)) # Cleanup trace sandbox dir
    
    print("\nSUCCESS: Phase 11 Sandboxing & Guard Layer Verified.")
    return True

if __name__ == "__main__":
    import sys
    # Initialize DB for standalone test if needed
    db.init_db()
    if not test_phase11_sandboxing():
        sys.exit(1)
