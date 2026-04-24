import sys
import os
import time
import logging
from logging.handlers import RotatingFileHandler

# Add core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from clide.storage import db
from clide.kernel.events import Event
from pie.inference import PieInference, PieModelEngine

# Setup Rotating Logger
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'introspection'))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_path = os.path.join(LOG_DIR, "introspection.log")
handler = RotatingFileHandler(log_path, maxBytes=1024 * 1024, backupCount=100)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("Introspection")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Also log to stdout for real-time visibility
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

def run_introspection_loop():
    logger.info("\n[*] Initiating Recursive Investigative Introspection Protocol...")
    
    # Fetch recent traces manually via DB
    try:
        with db.get_connection() as conn:
            rows = conn.execute("SELECT DISTINCT trace_id FROM events ORDER BY timestamp DESC LIMIT 5").fetchall()
            traces = [dict(row)["trace_id"] for row in rows]
    except Exception as e:
        logger.info(f"[!] Failed to fetch traces: {e}")
        return

    if not traces:
        logger.info("[!] No active traces found for introspection.")
        return

    engine = PieModelEngine()
    
    for trace_id in traces:
        logger.info(f"[*] Scoping Trace: {trace_id}")
        raw_events = db.get_events_by_trace(trace_id)
        if not raw_events:
            continue
            
        events = [Event.from_dict(e) for e in raw_events]
        
        # Run Inference with introspection flavour
        pie = PieInference(events, engine=engine)
        state = pie.analyze(active_flavours=["introspection"])
        
        # Check for Paradigm Shift Alignment
        flags = [f for f in state.anomaly_flags if "PARADIGM_SHIFT_REQUIRED" in f]
        if flags:
            logger.info(f"[!] ALIGNMENT PROTOCOL TRIGGERED FOR TRACE {trace_id}!")
            for f in flags:
                logger.info(f"    -> {f}")
            if "paradigm_shift" in state.diagnostic_report:
                logger.info(f"    -> Proposed Action: {state.diagnostic_report['paradigm_shift']['proposed_alignment']}")
        else:
            logger.info(f"[*] Trace {trace_id} aligns with optimal execution paradigm.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        logger.info("[*] Starting Autonomous Introspection Daemon (Infinite Recursive Loop)...")
        while True:
            run_introspection_loop()
            # Immediate recursion with minimal yield for system stability
            time.sleep(0.1)
    else:
        run_introspection_loop()
        logger.info("[*] Introspection protocol run completed.")
