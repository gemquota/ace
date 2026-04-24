import os
import time
from clide.kernel import identity, loop
from clide.storage import db

def test_phase19_identity_substrate():
    print("Initializing Phase 19 Identity & Substrate Test...")
    db.init_db()
    
    # 1. Test Genesis Hash Anchoring
    print("[*] Testing Genesis Hash initialization...")
    trace_id = "test_trace_19"
    genesis_hash = identity.init_genesis(trace_id)
    print(f"  Genesis Hash: {genesis_hash[:8]}...")
    
    if not genesis_hash or len(genesis_hash) != 64:
        print("[!] FAILED: Invalid Genesis Hash.")
        return False
        
    # Verify match
    if identity.verify_genesis():
        print("  SUCCESS: Genesis Hash verified across DB and .env.")
    else:
        print("[!] FAILED: Genesis Hash mismatch.")
        return False
        
    # 2. Test Substrate Migration Trigger
    print("[*] Testing Substrate Migration hardware trigger...")
    # Mock high CPU
    os.environ["CAP_SUBSTRATE_MIGRATE"] = "0"
    
    # We can't easily mock psutil within the loop thread, 
    # but we can manually set the env var and see if orchestrator picks it up.
    os.environ["CAP_SUBSTRATE_MIGRATE"] = "1"
    
    from clide.kernel.orchestrator import CapOrchestrator
    orch = CapOrchestrator()
    should_remote = orch._evaluate_compute_weight("stress_test", None)
    
    if should_remote:
        print("  SUCCESS: Substrate migration triggered by environment variable.")
    else:
        print("[!] FAILED: Substrate migration not triggered.")
        return False

    return True

if __name__ == "__main__":
    import sys
    os.environ["PYTHONPATH"] = "."
    if test_phase19_identity_substrate():
        print("[*] PHASE 19 TEST PASSED")
        sys.exit(0)
    else:
        print("[!] PHASE 19 TEST FAILED")
        sys.exit(1)
