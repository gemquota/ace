import time
import concurrent.futures
import threading
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from clide.schema import IntentDAG, ActionNode
from apc import executor
from clide.kernel import syscalls
from clide.types.event_types import Layer, EventType
from clide import task_queue as queue

class NodeStatus(Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class DAGScheduler:
    def __init__(
        self,
        trace_id: str,
        dag: IntentDAG,
        max_workers: int = 2,
        fail_fast: bool = True,
        use_queue: bool = False
    ):
        self.trace_id = trace_id
        self.dag = dag
        self.max_workers = max_workers
        self.fail_fast = fail_fast
        self.use_queue = use_queue
        
        # State tracking
        self.status: Dict[str, NodeStatus] = {a.action_id: NodeStatus.PENDING for a in dag.actions}
        self.nodes: Dict[str, ActionNode] = {a.action_id: a for a in dag.actions}
        self.retries: Dict[str, int] = {a.action_id: 0 for a in dag.actions}
        self.results: Dict[str, Any] = {}
        
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.stop_execution = False
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

    def update_dag(self, dag: IntentDAG):
        with self.lock:
            self.dag = dag
            for a in dag.actions:
                if a.action_id not in self.nodes:
                    self.nodes[a.action_id] = a
                    self.status[a.action_id] = NodeStatus.PENDING
                    self.retries[a.action_id] = 0

    def get_ready_nodes(self) -> List[ActionNode]:
        with self.lock:
            ready = []
            for node_id, status in self.status.items():
                if status == NodeStatus.PENDING:
                    node = self.nodes[node_id]
                    # Check dependencies
                    deps_met = True
                    for dep_id in node.dependencies:
                        if self.status.get(dep_id) != NodeStatus.SUCCESS:
                            deps_met = False
                            break
                    
                    if deps_met:
                        ready.append(node)
            
            # Sort by importance (descending)
            ready.sort(key=lambda x: x.importance, reverse=True)
            return ready

    def execute_async(self, node: ActionNode, causal_parent: str) -> concurrent.futures.Future:
        with self.lock:
            self.status[node.action_id] = NodeStatus.RUNNING
        
        if self.use_queue:
            task_id = queue.push_task(self.trace_id, {
                "action_id": node.action_id,
                "command": node.command
            }, causal_parent=causal_parent, priority=node.importance)
            
            # Return a real Future that is resolved by a background polling loop
            future = concurrent.futures.Future()
            threading.Thread(target=self._poll_task, args=(task_id, node.action_id, future), daemon=True).start()
            return future
        else:
            return self.pool.submit(self._execute_node_once, node, causal_parent)

    def _poll_task(self, task_id: str, node_id: str, future: concurrent.futures.Future):
        while True:
            from clide.storage import db
            with db.get_connection() as conn:
                row = conn.execute("SELECT status FROM task_queue WHERE task_id = ?", (task_id,)).fetchone()
                if row and row['status'] in ['SUCCESS', 'FAILED']:
                    exit_code = 0 if row['status'] == 'SUCCESS' else 1
                    res = {"exit_code": exit_code}
                    
                    with self.lock:
                        if exit_code == 0:
                            self.status[node_id] = NodeStatus.SUCCESS
                        else:
                            self.status[node_id] = NodeStatus.FAILED
                        self.results[node_id] = res
                    
                    future.set_result(res)
                    break
            time.sleep(0.5)

    def _execute_node_once(self, node: ActionNode, causal_parent: str) -> Dict[str, Any]:
        node_id = node.action_id
        
        # Emit ACTION_START
        start_id = syscalls.cap_event_commit(
            trace_id=self.trace_id,
            layer=Layer.CAP,
            event_type=EventType.ACTION_START,
            payload={"action_id": node_id, "command": node.command},
            causal_parent=causal_parent
        )

        res = executor.execute_command(
            trace_id=self.trace_id,
            command=node.command,
            causal_parent=start_id
        )
        
        with self.lock:
            if res["exit_code"] == 0:
                self.status[node_id] = NodeStatus.SUCCESS
            else:
                self.status[node_id] = NodeStatus.FAILED
            self.results[node_id] = res
            
        # Emit ACTION_COMPLETE
        status_str = "SUCCESS" if res["exit_code"] == 0 else "FAILED"
        syscalls.cap_event_commit(
            trace_id=self.trace_id,
            layer=Layer.CAP,
            event_type=EventType.ACTION_COMPLETE,
            payload={"action_id": node_id, "status": status_str, "exit_code": res["exit_code"]},
            causal_parent=res["complete_id"]
        )
        
        return res

    def is_complete(self) -> bool:
        with self.lock:
            return all(s in [NodeStatus.SUCCESS, NodeStatus.FAILED] for s in self.status.values())

    def run(self, initial_causal_parent: str):
        """Legacy blocking run method."""
        while not self.is_complete():
            ready = self.get_ready_nodes()
            if not ready:
                if any(s == NodeStatus.RUNNING for s in self.status.values()):
                    time.sleep(0.1)
                    continue
                else:
                    break
            
            futures = [self.execute_async(n, initial_causal_parent) for n in ready]
            concurrent.futures.wait(futures)
            
        return self.results

    def shutdown(self):
        self.pool.shutdown()
