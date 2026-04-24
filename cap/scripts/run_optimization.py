import os
import subprocess
import sys

def main():
    print("[*] Starting CAP Node Optimization...")
    project_root = "/data/data/com.termux/files/home/dev/cap"
    os.chdir(project_root)
    
    # 1. Refresh Mesh State
    print("[*] Refreshing Mesh State...")
    res = subprocess.run([sys.executable, "scripts/build_mesh_state.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[!] Failed to build mesh state")
        print(res.stderr)
        sys.exit(1)
        
    # 2. Prune task queue (Success/Failed entries)
    print("[*] Pruning task queue...")
    # Add pruning logic here if needed
    
    print("[+] Optimization Complete.")

if __name__ == "__main__":
    main()
