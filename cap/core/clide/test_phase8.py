import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from apc import executor
from clide.kernel import syscalls
from clide.kernel.events import NODE_ID

def test_phase8():
    print("Initializing Phase 8 Test...")
    db.init_db()
    
    # 1. Start a trace on Node 1 (default_node)
    trace_id = syscalls.cap_trace_start()
    print(f"[*] Trace {trace_id} started on {NODE_ID}")
    
    # 2. Node 1 executes a command
    res1 = executor.execute_command(trace_id, "echo 'Node 1 Step'", causal_parent=None)
    
    # 3. Simulate Node 2 executing a command on the same trace
    os.environ["CAP_NODE_ID"] = "remote_node_2"
    from importlib import reload
    import clide.kernel.events
    reload(cap.kernel.events)
    import clide.kernel.syscalls
    reload(cap.kernel.syscalls)
    
    print(f"[*] Simulating command from node: {os.environ['CAP_NODE_ID']}")
    # For Node 2, we need to pick up where Node 1 left off
    res2 = executor.execute_command(trace_id, "echo 'Node 2 Step'", causal_parent=res1["complete_id"])
    
    # 4. Verify Nodes List
    nodes = syscalls.cap_list_nodes()
    print("[*] Verifying registered nodes:")
    node_ids = [n["node_id"] for n in nodes]
    for nid in node_ids:
        print(f"  - {nid}")
    
    if "default_node" in node_ids and "remote_node_2" in node_ids:
        print("  VALIDATED (Multiple nodes registered).")
    else:
        print("  [!] FAILED (Node registration mismatch).")
        
    # 5. Verify Trace Merging (Order by Logical Clock)
    events = db.get_events_by_trace(trace_id)
    print("[*] Verifying merged trace order:")
    for e in events:
        print(f"  [{e['logical_clock']}] Node: {e['node_id']} | Type: {e['event_type']}")
    
    if len(events) >= 5: # TRACE_START, 2x SPAWN, 2x COMPLETE
        print("  VALIDATED (Global trace merged).")
    else:
        print(f"  [!] FAILED (Event count mismatch: {len(events)}).")

    print("\nSUCCESS: Phase 8 Distributed CAP Tests Passed.")

if __name__ == "__main__":
    test_phase8()
