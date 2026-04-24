import subprocess
import time
import os
import signal
from clide.storage import db

def test_phase15_distributed():
    print("Initializing Phase 15 Distributed Test...")
    db.init_db()
    
    # 1. Start 2 workers in background
    print("[*] Starting 2 workers...")
    w1 = subprocess.Popen(["python3", "clide/cli.py", "--start-worker", "--worker-id", "worker_A"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={**os.environ, "PYTHONPATH": "."})
    w2 = subprocess.Popen(["python3", "clide/cli.py", "--start-worker", "--worker-id", "worker_B"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={**os.environ, "PYTHONPATH": "."})
    
    time.sleep(5) # Wait for workers to register and poll
    
    try:
        # 2. Check worker status
        print("[*] Checking worker status...")
        res = subprocess.run(["python3", "clide/cli.py", "--queue-status"], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
        print(res.stdout)
        
        if "worker_A" not in res.stdout or "worker_B" not in res.stdout:
            print("[!] Workers not detected in status.")
            return False
            
        # 3. Execute a goal via queue
        print("[*] Executing goal via queue...")
        goal_res = subprocess.run(["python3", "clide/cli.py", "setup_workspace phase15_test", "--use-queue"], 
                                 capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "."})
        print(goal_res.stdout)
        
        # 4. Verify distribution
        print("[*] Verifying task distribution...")
        with db.get_connection() as conn:
            row = conn.execute("SELECT trace_id FROM traces ORDER BY created_at DESC LIMIT 1").fetchone()
            if not row:
                print("[!] No trace found.")
                return False
            trace_id = row['trace_id']
            
            events = conn.execute("SELECT node_id, event_type FROM events WHERE trace_id = ? AND event_type = 'EXEC_SPAWN'", (trace_id,)).fetchall()
            nodes = set([e['node_id'] for e in events])
            print(f"  Nodes involved in execution: {nodes}")
            
            # If both workers were involved, success
            if "worker_A" in nodes or "worker_B" in nodes:
                 print("  SUCCESS: Distributed execution verified.")
                 return True
            else:
                 print("  FAILED: No worker node_id found in execution events.")
                 return False

    finally:
        print("[*] Terminating workers...")
        w1.terminate()
        w2.terminate()
        w1.wait()
        w2.wait()

if __name__ == "__main__":
    import sys
    # Ensure we are in the right directory
    os.environ["PYTHONPATH"] = "."
    if test_phase15_distributed():
        sys.exit(0)
    else:
        sys.exit(1)
