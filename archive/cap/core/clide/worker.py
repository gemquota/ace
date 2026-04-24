import time
import os
import signal
import sys
from clide import task_queue as queue
from apc import executor
from clide.kernel import syscalls

NODE_ID = os.environ.get("CAP_NODE_ID", f"worker_{os.getpid()}")
POLL_INTERVAL = 2 # seconds

class CapWorker:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.running = True
        self.active_tasks = 0

    def stop(self, signum, frame):
        print(f"[*] Worker {self.node_id} shutting down...")
        self.running = False

    def run(self):
        print(f"[*] Worker {self.node_id} started. Polling for tasks...")
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        while self.running:
            # 1. Heartbeat
            queue.worker_heartbeat(self.node_id, self.active_tasks)
            
            # 2. Cleanup stale tasks (one worker can do this, or all periodically)
            queue.requeue_stale_tasks()
            
            # 3. Poll for task
            task = queue.claim_task(self.node_id)
            
            if task:
                self.active_tasks += 1
                queue.worker_heartbeat(self.node_id, self.active_tasks)
                
                print(f"[*] Worker {self.node_id} CLAIMED task {task['task_id'][:8]}: {task['action_payload']['command']}")
                
                try:
                    # Execute action via APC
                    # We need to set the environment variable so execute_command uses our node_id
                    os.environ["CAP_NODE_ID"] = self.node_id
                    
                    res = executor.execute_command(
                        trace_id=task['trace_id'],
                        command=task['action_payload']['command'],
                        causal_parent=task['causal_parent']
                    )
                    
                    success = res['exit_code'] == 0
                    queue.complete_task(task['task_id'], success)
                    print(f"[*] Worker {self.node_id} COMPLETED task {task['task_id'][:8]} (Success: {success})")
                    
                except Exception as e:
                    print(f"[!] Worker {self.node_id} FAILED task {task['task_id'][:8]}: {e}")
                    queue.complete_task(task['task_id'], False)
                
                finally:
                    self.active_tasks -= 1
                    queue.worker_heartbeat(self.node_id, self.active_tasks)
            else:
                time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    worker = CapWorker(NODE_ID)
    worker.run()
