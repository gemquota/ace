import os
import sys
import json
import time
import requests
import subprocess

# Configuration
API_BASE = "http://127.0.0.1:8080/api"
APC_DIR = os.path.expanduser("~/dev/apc")

def process_arm_queue():
    print(f"[*] ARM_WORKER: Monitoring {API_BASE}/arm/tasks...")
    while True:
        try:
            # 1. Fetch pending tasks
            resp = requests.get(f"{API_BASE}/arm/tasks")
            if resp.status_code == 200:
                tasks = resp.json()
                for task in tasks:
                    task_id = task["task_id"]
                    payload = json.loads(task["action_payload"])
                    command = payload.get("command")
                    
                    print(f"[*] ARM_WORKER: Intercepted task {task_id[:8]} -> '{command}'")
                    
                    # 2. Execute the deterministic code (the "Skill" part)
                    # We use the real executor logic here via the API or directly.
                    # User said: "ARM mode isnt meant to be manual user driven its meant to have skills for gemini cli to perform the deterministic code"
                    # So the worker (Gemini Skill) performs it.
                    
                    print(f"[*] ARM_WORKER: Executing deterministic skill for task...")
                    exec_resp = requests.post(f"{API_BASE}/arm/execute/{task_id}")
                    if exec_resp.status_code == 200:
                        print(f"[*] ARM_WORKER: Task handed off to APC executor.")
                    else:
                        print(f"[!] ARM_WORKER: Handoff failed: {exec_resp.text}")
            
        except Exception as e:
            print(f"[!] ARM_WORKER Error: {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    process_arm_queue()
