import os
import json
from clide.meta.model import SelfArchitectureModel
from clide.meta.evaluator import ArchitectureEvaluator

def test_phase18_meta_cognition():
    print("Initializing Phase 18 Meta-Cognition Test...")
    
    # 1. Initialize Model
    model = SelfArchitectureModel()
    
    # 2. Update Subsystem Metrics
    print("[*] Updating subsystem metrics (simulating low efficiency for APC)...")
    model.update_metrics("APC", {"efficiency": 0.4, "error_count": 5})
    model.update_metrics("PIE", {"success_rate": 0.9})
    
    # 3. Evaluate Architecture
    evaluator = ArchitectureEvaluator(model)
    proposals = evaluator.evaluate()
    
    print(f"[*] Evaluation generated {len(proposals)} proposals.")
    
    # Check for specific proposal based on low efficiency
    found_throttle = False
    for p in proposals:
        if p["subsystem"] == "APC" and p["type"] == "THROTTLE":
            found_throttle = True
            print("  SUCCESS: APC Throttling proposal generated due to low efficiency.")
            break
            
    if not found_throttle:
        print("[!] FAILED: Expected APC THROTTLE proposal not found.")
        return False
        
    # 4. Meta-Goals
    meta_goals = evaluator.get_meta_goals()
    print(f"[*] Meta-Goals: {meta_goals}")
    if any(g["primitive"] == "diagnose_apc" for g in meta_goals):
        print("  SUCCESS: Meta-Goal for APC diagnosis generated.")
    else:
        print("[!] FAILED: Expected Meta-Goal 'diagnose_apc' not found.")
        return False

    # 5. Save and Load
    model.save("test_arch_model.json")
    loaded = SelfArchitectureModel.load("test_arch_model.json")
    if loaded.subsystems["APC"].metrics["efficiency"] == 0.4:
        print("  SUCCESS: Model persistence verified.")
    else:
        print("[!] FAILED: Model persistence mismatch.")
        return False

    if os.path.exists("test_arch_model.json"):
        os.remove("test_arch_model.json")
        
    return True

if __name__ == "__main__":
    import sys
    os.environ["PYTHONPATH"] = "."
    if test_phase18_meta_cognition():
        print("[*] PHASE 18 TEST PASSED")
        sys.exit(0)
    else:
        print("[!] PHASE 18 TEST FAILED")
        sys.exit(1)
