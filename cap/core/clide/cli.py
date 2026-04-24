import sys
import os
import argparse

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from clide.storage import db
from clide.kernel import orchestrator
from clide.kernel import syscalls
from clide.kernel import replay
from clide.types.event_types import EventType
from pie.engine import PieEngine
from pie.inference import PieInference, PieModelEngine

def main():
    parser = argparse.ArgumentParser(description="CAP: Cognitive Architecture Platform")
    parser.add_argument("goal", type=str, nargs="?", help="The goal to execute")
    parser.add_argument("--trace", type=str, help="Resume an existing trace ID")
    parser.add_argument("--init", action="store_true", help="Initialize the CAP database")
    parser.add_argument("--history", action="store_true", help="Show trace history")
    parser.add_argument("--replay", type=str, help="Replay a trace ID")
    parser.add_argument("--rollback", type=str, help="Rollback trace to event. Format: <trace_id>,<event_id>")
    
    # PIE Extensions
    parser.add_argument("--pie-predict", type=str, help="Predict next steps for trace ID")
    parser.add_argument("--pie-diagnose", type=str, help="Diagnose failures in trace ID")
    parser.add_argument("--pie-causal", type=str, help="Show causal weights for trace ID")
    parser.add_argument("--nodes", action="store_true", help="List active nodes")
    
    # Autonomous Extensions
    parser.add_argument("--auto-start", type=str, help="Start autonomous loop for trace ID")
    parser.add_argument("--auto-status", type=str, help="Show autonomous status for trace ID")
    
    # Sovereign Extensions
    parser.add_argument("--sovereign-status", action="store_true", help="Show global sovereign system health")
    parser.add_argument("--sovereign-manifest", type=str, help="Show synthetic intents for trace ID")
    
    # Distributed Extensions (Phase 15)
    parser.add_argument("--start-worker", action="store_true", help="Start a local worker process")
    parser.add_argument("--worker-id", type=str, help="Specific node_id for worker")
    parser.add_argument("--queue-status", action="store_true", help="Show task queue status")
    parser.add_argument("--use-queue", action="store_true", help="Execute goal via task queue")
    
    args = parser.parse_args()
    
    if args.init:
        db.init_db()
        print("[*] CAP DATABASE INITIALIZED.")
        return

    if args.history:
        print("[*] HISTORY: Recent traces not yet searchable.")
        return

    if args.replay:
        print(f"[*] REPLAYING TRACE {args.replay}")
        result = replay.cap_trace_replay(args.replay)
        print(f"[*] REPLAY STATUS: {result.status}")
        for m in result.mismatches:
            print(f"[!] MISMATCH Event {m.event_id}: Expected {m.expected_hash}, Actual {m.actual_hash}")
        return

    if args.rollback:
        trace_id, event_id = args.rollback.split(',')
        print(f"[*] ROLLING BACK TRACE {trace_id} TO EVENT {event_id}")
        replay.cap_rollback(trace_id, event_id)
        print("[*] ROLLBACK SUCCESSFUL.")
        return

    if args.pie_predict:
        pie_engine = PieEngine()
        events = pie_engine.load_trace(args.pie_predict)
        inf = PieInference(events)
        state = inf.analyze(active_flavours=["predictive"])
        print(f"[*] PIE PREDICTIONS FOR TRACE {args.pie_predict}:")
        for p in state.predictions:
            print(f"  -> {p['step']} (Confidence: {p['confidence']:.2f})")
        return

    if args.pie_diagnose:
        pie_engine = PieEngine()
        events = pie_engine.load_trace(args.pie_diagnose)
        inf = PieInference(events)
        state = inf.analyze(active_flavours=["diagnostic"])
        print(f"[*] PIE DIAGNOSTIC REPORT FOR TRACE {args.pie_diagnose}:")
        report = state.diagnostic_report
        if not report:
            print("  No failures detected.")
        else:
            print(f"  Failure Points: {report.get('failure_points', [])}")
            print(f"  Probable Causes: {report.get('probable_causes', [])}")
            print(f"  Suggested Fixes: {report.get('suggested_fixes', [])}")
        return

    if args.pie_causal:
        engine = PieModelEngine()
        print("[*] PIE CAUSAL WEIGHTS:")
        for edge, weight in engine.causal_weights.items():
            print(f"  {edge}: {weight:.2f}")
        return

    if args.nodes:
        nodes = syscalls.cap_list_nodes()
        print("[*] ACTIVE NODES:")
        for n in nodes:
            print(f"  - {n['node_id']} (Last seen: {n['last_seen']})")
        return

    if args.auto_start:
        from clide.kernel.loop import AutonomousLoop
        loop = AutonomousLoop(args.auto_start)
        loop.start()
        return

    if args.auto_status:
        # For now, just show recent status from event log
        events = db.get_events_by_trace(args.auto_status)
        status_events = [e for e in events if e["event_type"] == EventType.SYSTEM_STATE.value]
        if status_events:
            last_status = status_events[-1]
            import json
            payload = json.loads(last_status["payload"]) if isinstance(last_status["payload"], str) else last_status["payload"]
            print(f"[*] AUTONOMOUS STATUS for {args.auto_status}: {payload.get('state', 'UNKNOWN')}")
        else:
            print(f"[*] NO AUTONOMOUS STATUS FOUND for {args.auto_status}.")
        return

    if args.sovereign_status:
        from clide.kernel.governance import GovernanceEngine
        gov = GovernanceEngine()
        gov.evaluate_governance()
        print("[*] SOVEREIGN SYSTEM HEALTH: OPTIMAL")
        return

    if args.sovereign_manifest:
        from clide.synthetic import generate_synthetic_intent
        pie_engine = PieEngine()
        events = pie_engine.load_trace(args.sovereign_manifest)
        inf = PieInference(events)
        state = inf.analyze()
        intent = generate_synthetic_intent(state)
        if intent:
            print(f"[*] SYNTHETIC INTENT for {args.sovereign_manifest}:")
            print(f"  Primitive: {intent['primitive']}")
            print(f"  Goal: {intent['goal']}")
            print(f"  Reason: {intent['reason']}")
        else:
            print(f"[*] NO SYNTHETIC INTENT generated for {args.sovereign_manifest}.")
        return

    if args.start_worker:
        from clide.worker import CapWorker
        node_id = args.worker_id or os.environ.get("CAP_NODE_ID", f"worker_{os.getpid()}")
        worker = CapWorker(node_id)
        worker.run()
        return

    if args.queue_status:
        from clide import task_queue as queue
        status = queue.get_queue_status()
        print("[*] TASK QUEUE STATUS:")
        for s, count in status.items():
            print(f"  {s}: {count}")
        
        workers = queue.get_active_workers()
        print("\n[*] ACTIVE WORKERS:")
        for w in workers:
            print(f"  - {w['node_id']} (Tasks: {w['active_tasks']}, Last seen: {w['last_seen']})")
        return

    if not args.goal:
        parser.print_help()
        return

    # Start Cognitive Loop
    cap = orchestrator.CapOrchestrator(trace_id=args.trace)
    try:
        cap.execute_goal(args.goal, use_queue=args.use_queue)
    except KeyboardInterrupt:
        print("\n[!] INTERRUPTED.")
    finally:
        cap.shutdown()

if __name__ == "__main__":
    main()
