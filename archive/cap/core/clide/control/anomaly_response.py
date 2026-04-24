from enum import Enum
from typing import List, Dict, Any, Optional

class ResponseLevel(Enum):
    LEVEL_1_ALERT = 1
    LEVEL_2_THROTTLE = 2
    LEVEL_3_ISOLATION = 3
    LEVEL_4_ROLLBACK = 4

class AnomalyResponseSystem:
    """
    Graduated Anomaly Response System.
    Prevents overreaction instability.
    """
    def __init__(self, controller: Any):
        self.controller = controller

    def handle_anomaly(self, anomaly_id: str, severity: float, payload: Dict[str, Any]):
        """
        Determines and executes the appropriate response level.
        """
        level = self._determine_level(severity)
        print(f"[!] ANOMALY: {anomaly_id} detected. Severity: {severity}. Escalating to {level.name}")
        
        if level == ResponseLevel.LEVEL_1_ALERT:
             self._execute_alert(anomaly_id, payload)
        elif level == ResponseLevel.LEVEL_2_THROTTLE:
             self._execute_throttle(anomaly_id, payload)
        elif level == ResponseLevel.LEVEL_3_ISOLATION:
             self._execute_isolation(anomaly_id, payload)
        elif level == ResponseLevel.LEVEL_4_ROLLBACK:
             self._execute_rollback(anomaly_id, payload)

    def _determine_level(self, severity: float) -> ResponseLevel:
        if severity < 0.3: return ResponseLevel.LEVEL_1_ALERT
        if severity < 0.6: return ResponseLevel.LEVEL_2_THROTTLE
        if severity < 0.8: return ResponseLevel.LEVEL_3_ISOLATION
        return ResponseLevel.LEVEL_4_ROLLBACK

    def _execute_alert(self, aid: str, payload: Dict[str, Any]):
        print(f"[*] RESPONSE: LEVEL 1: Logging anomaly {aid}")
        # Log event...
        
    def _execute_throttle(self, aid: str, payload: Dict[str, Any]):
        print(f"[*] RESPONSE: LEVEL 2: Throttling spawning and task execution.")
        # Apply policies via controller...
        
    def _execute_isolation(self, aid: str, payload: Dict[str, Any]):
        print(f"[*] RESPONSE: LEVEL 3: Isolating affected agents {payload.get('agent_ids', [])}")
        # Terminate or isolate agents...
        
    def _execute_rollback(self, aid: str, payload: Dict[str, Any]):
        print(f"[*] RESPONSE: LEVEL 4: Initiating system rollback.")
        # Trigger rollback via controller...
