from typing import List, Dict, Any

class SemanticPrimitives:
    ONTOLOGY = {
        "setup_workspace": [
            {"cmd": "mkdir -p {name}", "importance": 10.0},
            {"cmd": "cd {name}", "importance": 8.0},
            {"cmd": "git init", "importance": 5.0}
        ],
        "test_project": [
            {"cmd": "pytest", "importance": 10.0},
            {"cmd": "python3 -m unittest", "importance": 9.0}
        ],
        "clean_cache": [
            {"cmd": "rm -rf __pycache__", "importance": 3.0},
            {"cmd": "find . -name '*.pyc' -delete", "importance": 2.0}
        ],
        "generate_report": [
            {"cmd": "python3 scripts/generate_report.py", "importance": 10.0}
        ],
        "default": [
            {"cmd": "{goal}", "importance": 5.0}
        ]
    }

    @classmethod
    def get_actions(cls, key: str) -> List[Dict[str, Any]]:
        return cls.ONTOLOGY.get(key, cls.ONTOLOGY["default"])
        
    @classmethod
    def add_primitive(cls, key: str, actions: List[Dict[str, Any]]):
        cls.ONTOLOGY[key] = actions
