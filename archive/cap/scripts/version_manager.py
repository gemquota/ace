import os
import sys

APC_DIR = os.path.expanduser("~/dev/apc")
VERSION_PATH = os.path.join(APC_DIR, "VERSION")

def get_version():
    if os.path.exists(VERSION_PATH):
        with open(VERSION_PATH, "r") as f:
            return f.read().strip()
    return "0.0.0"

def bump_version(part="patch"):
    version = get_version()
    major, minor, patch = map(int, version.split('.'))
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
        
    new_version = f"{major}.{minor}.{patch}"
    with open(VERSION_PATH, "w") as f:
        f.write(new_version)
    return new_version

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "get":
            print(get_version())
        elif action == "bump":
            part = sys.argv[2] if len(sys.argv) > 2 else "patch"
            print(f"Bumping {part}... New version: {bump_version(part)}")
    else:
        print(f"Current Version: {get_version()}")
