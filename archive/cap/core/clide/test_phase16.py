import os
import time
import json
from clide.kernel import syscalls
from clide.kernel.orchestrator import CapOrchestrator
from clide.memory.store import MemoryStore
from clide.storage import db

def test_phase16_memory_persistence():
    print("Initializing Phase 16 Cognitive Memory Test...")
    db.init_db()
    memory = MemoryStore()
    
    # 1. Start a trace and execute a simple goal
    orch = CapOrchestrator()
    trace_id = orch.trace_id
    goal = "echo 'memory_test' > memory.txt"
    
    print(f"[*] Executing goal: {goal}")
    inf = orch.execute_goal(goal)
    
    # 2. Verify sequence is stored in memory
    print("[*] Verifying memory persistence...")
    sequences = memory.get_successful_sequences("default") # Default primitive
    found = False
    for seq in sequences:
        if "echo 'memory_test' > memory.txt" in json.loads(seq['command_sequence']):
            found = True
            print(f"  SUCCESS: Sequence found in memory (Weight: {seq['weight']})")
            break
    
    if not found:
        print("[!] FAILED: Sequence not found in memory.")
        return False
        
    # 3. Verify pattern weighting
    print("[*] Verifying pattern weighting...")
    # Get hash of the command
    import hashlib
    cmd = "echo 'memory_test' > memory.txt"
    cmd_hash = hashlib.sha256(cmd.encode()).hexdigest()
    with memory.get_connection() as conn:
        row = conn.execute("SELECT weight FROM pattern_weights WHERE pattern_hash = ?", (cmd_hash,)).fetchone()
        if row and row['weight'] > 1.0:
            print(f"  SUCCESS: Pattern weight increased to {row['weight']}")
        else:
            print(f"  FAILED: Pattern weight not increased. Current: {row['weight'] if row else 'None'}")
            return False

    # Cleanup
    if os.path.exists("memory.txt"):
        os.remove("memory.txt")
        
    return True

if __name__ == "__main__":
    import sys
    os.environ["PYTHONPATH"] = "."
    if test_phase16_memory_persistence():
        print("[*] PHASE 16 TEST PASSED")
        sys.exit(0)
    else:
        print("[!] PHASE 16 TEST FAILED")
        sys.exit(1)
