import os
import time
from clide.kernel import syscalls
from clide.sovereign.engine import SovereignGoalEngine
from pie.inference import InferenceState
from clide.storage import db

def test_phase17_sovereign_goals():
    print("Initializing Phase 17 Sovereign Engine Test...")
    db.init_db()
    
    # 1. Mock an inference state with an anomaly
    inf_state = InferenceState(trace_id="test_trace_17")
    inf_state.anomaly_flags.append("HISTORICAL_FAILURE_MATCH")
    inf_state.execution_summary["total_commands"] = 10
    inf_state.execution_summary["success_rate"] = 0.9

    # 2. Generate goals
    sovereign = SovereignGoalEngine(trace_id="test_trace")
    goals = sovereign.generate_goals(inf_state)
    
    print(f"[*] Generated {len(goals)} goals.")
    
    # Check for anomaly-driven goal
    found_fix = False
    found_opt = False
    for g in goals:
        if g.primitive == "fix_repeated_failures":
            found_fix = True
        if g.primitive == "optimize_paths":
            found_opt = True
            
    if found_fix and found_opt:
        print("  SUCCESS: Both anomaly-driven and optimization goals generated.")
    else:
        print(f"  FAILED: Missing goals. Fix={found_fix}, Opt={found_opt}")
        return False
        
    # 3. Select next goal
    next_goal = sovereign.select_next_goal()
    if next_goal and next_goal.priority == 0.9:
        print(f"  SUCCESS: Highest priority goal selected: {next_goal.primitive}")
    else:
        print(f"  FAILED: Incorrect goal selection. Priority: {next_goal.priority if next_goal else 'None'}")
        return False

    return True

if __name__ == "__main__":
    import sys
    os.environ["PYTHONPATH"] = "."
    if test_phase17_sovereign_goals():
        print("[*] PHASE 17 TEST PASSED")
        sys.exit(0)
    else:
        print("[!] PHASE 17 TEST FAILED")
        sys.exit(1)
