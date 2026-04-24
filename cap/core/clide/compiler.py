import json
import sqlite3
import os
import uuid
from typing import List, Dict, Any, Optional
from .schema import ActionNode, IntentDAG
from .ontology import SemanticPrimitives
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from pie.inference import InferenceState
from clide.memory.retrieval import HybridRetriever

class IntentCompiler:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or syscalls.cap_trace_start()
        self.context = {}
        self.retriever = HybridRetriever()

    def inject_context(self, state: InferenceState):
        self.context["inferred_intents"] = state.intent_hypotheses
        self.context["anomaly_flags"] = state.anomaly_flags
        self.context["last_summary"] = state.execution_summary

    def _forge_tool(self, tool_name: str, goal: str):
        import hashlib
        
        # Simplified forging logic: write a script that echoes the goal
        script_code = f"# Forged Tool: {tool_name}\n# Goal: {goal}\nprint('Executing forged tool: {tool_name}')\n"
        script_hash = hashlib.sha256(script_code.encode('utf-8')).hexdigest()
        
        tool_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")
        os.makedirs(tool_dir, exist_ok=True)
        script_path = os.path.join(tool_dir, f"{tool_name}_{script_hash[:8]}.py")
        
        with open(script_path, "w") as f:
            f.write(script_code)
            
        # Append to ontology
        SemanticPrimitives.add_primitive(tool_name, [
            {"cmd": f"python3 {script_path}", "importance": 10.0, "is_literal": True}
        ])
        print(f"[*] TOOL FORGED: {tool_name} (Hash: {script_hash[:8]})")

    def _fetch_db_intent(self, intent_name: str) -> Optional[List[Dict[str, Any]]]:
        swarm_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cap_swarm.db")
        if not os.path.exists(swarm_db):
            return None
        try:
            with sqlite3.connect(swarm_db) as conn:
                row = conn.execute("SELECT actions FROM intents WHERE name = ?", (intent_name,)).fetchone()
                if row:
                    return json.loads(row[0])
        except Exception as e:
            print(f"[!] Error fetching DB intent: {e}")
        return None

    def compile(self, goal: str, causal_parent: Optional[str] = None) -> IntentDAG:
        primitive_key = "default"
        params = {"goal": goal}
        
        # First check the intent database
        db_actions = self._fetch_db_intent(goal)
        if db_actions:
            primitive_key = goal
            templates = db_actions
        else:
            if "forge tool" in goal.lower():
                tool_name = goal.split()[-1] if len(goal.split()) > 2 else "forged_tool"
                self._forge_tool(tool_name, goal)
                primitive_key = tool_name
            elif "setup" in goal.lower():
                primitive_key = "setup_workspace"
                params["name"] = goal.split()[-1] if len(goal.split()) > 1 else "project"
            elif "assess" in goal.lower() or "report" in goal.lower():
                primitive_key = "generate_report"
            elif "test" in goal.lower() and "echo" not in goal.lower():
                primitive_key = "test_project"
            elif "clean" in goal.lower():
                primitive_key = "clean_cache"
            
            templates = SemanticPrimitives.get_actions(primitive_key)
            
            # If it's a default single command, make it execute in bash for real functionality
            if primitive_key == "default" and len(templates) == 1:
                templates = [{"cmd": f"bash -c {json.dumps(goal)}", "importance": 5.0, "is_literal": True}]

        actions = []
        
        # Phase 16: Check memory for successful historical overrides
        history = self.retriever.get_candidate_sequences(primitive_key)
        if history and not db_actions: # Don't override purchased DB intents with local history
            print(f"[*] MEMORY HIT: Using best historical sequence for {primitive_key}")
            templates = [{"cmd": cmd, "importance": 1.0, "is_literal": True} for cmd in history[0]]

        last_id = None
        for i, t in enumerate(templates):
            action_id = f"action_{i}_{str(uuid.uuid4())[:8]}"
            cmd = t["cmd"] if t.get("is_literal") else t["cmd"].format(**params)
            
            node = ActionNode(
                action_id=action_id,
                command=cmd,
                dependencies=[last_id] if last_id else [],
                importance=t["importance"]
            )
            actions.append(node)
            last_id = action_id
            
        dag = IntentDAG(
            intent_id=str(uuid.uuid4()),
            goal=goal,
            actions=actions,
            context_refs=[self.trace_id],
            metadata={"primitive": primitive_key}
        )
        
        # 3. Emit INTENT_CREATE event
        syscalls.cap_event_commit(
            trace_id=self.trace_id,
            layer=Layer.CLIDE,
            event_type=EventType.INTENT_CREATE,
            payload=dag.to_dict(),
            causal_parent=causal_parent
        )
        
        return dag
