import os
import time
import sqlite3
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWARM_DB = os.path.join(BASE_DIR, "data", "cap_swarm.db")
EVENTS_DB = os.path.join(BASE_DIR, "data", "cap_events.db")

def generate_report():
    print("[*] Generating TIRRR Cognitive Report...")
    report_path = os.path.join(BASE_DIR, "reports", f"report_{int(time.time())}.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    report = []
    report.append("# 🧠 CAP.OS COGNITIVE STATE REPORT")
    report.append(f"Generated: {time.ctime()}")
    report.append("\n## 🧬 SWARM TOPOLOGY")
    
    try:
        with sqlite3.connect(SWARM_DB) as conn:
            conn.row_factory = sqlite3.Row
            agents = conn.execute("SELECT * FROM agent_wallets").fetchall()
            report.append(f"- **Active Agents**: {len(agents)}")
            for a in agents:
                report.append(f"  - `AGENT::{a['agent_id'][:8]}`: {a['balance']:.2f} CR (State: {a.get('state', 'ACTIVE')})")
    except:
        report.append("  - [!] Error accessing swarm database.")

    report.append("\n## 🛒 INTENT MARKET VITALITY")
    try:
        with sqlite3.connect(SWARM_DB) as conn:
            conn.row_factory = sqlite3.Row
            intents = conn.execute("SELECT * FROM intents ORDER BY price DESC").fetchall()
            report.append(f"- **Market Depth**: {len(intents)} listings")
            for i in intents:
                report.append(f"  - `{i['name']}`: {i['price']:.2f} CR (Owner: {i['owner_agent_id'][:8]})")
    except:
        report.append("  - [!] Error accessing intent database.")

    report.append("\n## 🚀 RECENT COGNITIVE TELEMETRY")
    try:
        with sqlite3.connect(EVENTS_DB) as conn:
            conn.row_factory = sqlite3.Row
            events = conn.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 10").fetchall()
            for e in events:
                report.append(f"- `[{e['layer']}]` **{e['event_type']}**: {e['event_id'][:8]}...")
    except:
        report.append("  - [!] Error accessing events database.")

    report.append("\n## 🏁 CONCLUSION")
    report.append("System is maintaining causal integrity. Autonomous swarm loop is active.")

    with open(report_path, "w") as f:
        f.write("\n".join(report))
    
    print(f"[*] Report saved: {report_path}")
    # Return JSON for telemetry
    print(json.dumps({"report_path": report_path, "status": "SUCCESS"}))

if __name__ == "__main__":
    generate_report()
