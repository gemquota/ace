import os
import json
import hashlib
from typing import Dict, Any, Optional
from apc.executor import execute_python_script

def generate_tkinter_script(ui_layout: str) -> str:
    """Generate a Tkinter script based on a generic layout description."""
    return f"""
import tkinter as tk
import json

def on_action():
    # Capture state or perform action
    state = {{"action": "clicked", "status": "success", "layout": "{ui_layout}"}}
    print(json.dumps(state))
    root.destroy()

root = tk.Tk()
root.title("CAP X11 Bridge")
# Simplified dynamic UI generation
lbl = tk.Label(root, text="Layout: {ui_layout}")
lbl.pack()
btn = tk.Button(root, text="Action", command=on_action)
btn.pack()

# Autoclick for automated testing/headless
root.after(1000, on_action)
root.mainloop()
"""

def generate_pyqt_script(ui_layout: str) -> str:
    """Generate a PyQt script."""
    return f"""
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer

def on_action():
    state = {{"action": "clicked", "status": "success", "layout": "{ui_layout}"}}
    print(json.dumps(state))
    QApplication.instance().quit()

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("CAP X11 Bridge")
layout = QVBoxLayout()
lbl = QLabel("Layout: {ui_layout}")
layout.addWidget(lbl)
btn = QPushButton("Action")
btn.clicked.connect(on_action)
layout.addWidget(btn)
window.setLayout(layout)

# Autoclick for automated testing/headless
QTimer.singleShot(1000, on_action)

window.show()
sys.exit(app.exec_())
"""

def run_x11_script(script_code: str, display: str = ":1", framework: str = "tkinter") -> Dict[str, Any]:
    """
    Run an X11 script targeting the specified display and capture its JSON output to generate a state hash.
    """
    os.environ["DISPLAY"] = display
    
    script_path = f"/tmp/cap_x11_script_{os.getpid()}.py"
    with open(script_path, "w") as f:
        f.write(script_code)
    
    try:
        # We could use execute_python_script here, but it doesn't run in a separate process that respects os.environ["DISPLAY"] easily unless set before p.start()
        # Since os.environ is inherited, it should work.
        result = execute_python_script(script_path, timeout_seconds=15)
        
        # Parse JSON output from stdout to generate post_state_hash
        post_state_hash = "n/a"
        parsed_payload = {}
        for line in result["stdout"].splitlines():
            try:
                parsed_payload = json.loads(line)
                # Generate post_state_hash from JSON
                post_state_hash = hashlib.sha256(line.encode('utf-8')).hexdigest()
                break
            except json.JSONDecodeError:
                pass
                
        return {
            "success": result["exit_code"] == 0,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "json_payload": parsed_payload,
            "post_state_hash": post_state_hash,
            "timeout": result["timeout_flag"]
        }
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
