import sys
import os
import shutil

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from clide.kernel import orchestrator

def test_full_cognitive_loop():
    print("\nInitializing Phase 5 Test...")
    db.init_db()
    
    # 1. Start Orchestrator
    cap = orchestrator.CapOrchestrator()
    trace_id = cap.trace_id
    
    # 2. Execute a complex goal
    print(f"\n[Test 1] Executing goal: setup_workspace phase5_demo")
    inference1 = cap.execute_goal("setup_workspace phase5_demo")
    
    # Verify first pass
    if "directory setup" not in [i["label"] for i in inference1.intent_hypotheses]:
        print("  FAILED: Intent 'directory setup' not inferred")
        return False
        
    # 3. Execute another goal in the SAME trace (demonstrating loop)
    print(f"\n[Test 2] Executing goal: clean_cache")
    inference2 = cap.execute_goal("clean_cache")
    
    # Verify second pass
    if inference2.execution_summary["total_commands"] < 3: # cumulative
        print(f"  FAILED: Commands not accumulated in trace. Got {inference2.execution_summary['total_commands']}")
        return False

    cap.shutdown()
    
    # Cleanup
    if os.path.exists("phase5_demo"):
        shutil.rmtree("phase5_demo")

    print("\nSUCCESS: Phase 5 Full Cognitive Loop Verified.")
    return True

if __name__ == "__main__":
    if test_full_cognitive_loop():
        sys.exit(0)
    else:
        sys.exit(1)
