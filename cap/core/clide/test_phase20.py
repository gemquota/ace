import os
import time
from clide.swarm.manager import SwarmManager, AgentState
from clide.storage import db

def test_phase20_swarm_economy():
    print("Initializing Phase 20 Swarm Economy Test...")
    db.init_db()
    
    manager = SwarmManager()
    
    # 1. Spawn Agent
    agent_id = manager.spawn_agent("test_agent")
    agent = manager.agents[agent_id]
    
    print(f"[*] Agent Spawned: {agent_id[:8]} Balance: {agent.economy.get_balance()}")
    
    # 2. Spend Credits
    print("[*] Simulating task execution (spending 20 credits)...")
    if agent.economy.spend(20.0, "TEST_TASK"):
        print(f"  SUCCESS: Spent 20.0 credits. Balance: {agent.economy.get_balance()}")
    else:
        print("[!] FAILED: Could not spend credits.")
        return False
        
    # 3. Earn Credits (Success Bonus)
    print("[*] Simulating task success (earning 10.0 bonus)...")
    agent.update_performance(success_rate=1.0, cost_efficiency=0.8)
    print(f"  SUCCESS: New balance after bonus: {agent.economy.get_balance()}")
    if agent.economy.get_balance() == 90.0: # 100 - 20 + 10
        print("  SUCCESS: Balance calculation correct.")
    else:
        print(f"[!] FAILED: Incorrect balance calculation. Expected 90.0, got {agent.economy.get_balance()}")
        return False
        
    # 4. Evolutionary Pressure
    print("[*] Testing Evolutionary Pruning...")
    # Spawn a low-performer and bankrupt them
    bad_agent_id = manager.spawn_agent("bad_agent")
    bad_agent = manager.agents[bad_agent_id]
    bad_agent.economy.spend(100.0, "GAMBLING")
    bad_agent.update_performance(success_rate=0.0, cost_efficiency=0.0)
    
    print(f"[*] Bad Agent State before evolution: {bad_agent.state.value}")
    manager.trigger_evolution()
    
    if bad_agent_id not in manager.agents:
        print("  SUCCESS: Low-performer pruned during evolution.")
    else:
        print(f"[!] FAILED: Bad agent still in swarm. State: {manager.agents[bad_agent_id].state.value}")
        return False

    return True

if __name__ == "__main__":
    import sys
    os.environ["PYTHONPATH"] = "."
    if test_phase20_swarm_economy():
        print("[*] PHASE 20 TEST PASSED")
        sys.exit(0)
    else:
        print("[!] PHASE 20 TEST FAILED")
        sys.exit(1)
