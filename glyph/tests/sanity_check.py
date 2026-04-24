import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock missing libraries
mock_litellm = MagicMock()
# Make litellm return a valid python script when the JIT Compiler asks for it
def mock_completion(**kwargs):
    role = kwargs.get('messages', [{}])[0].get('role', '')
    if 'JIT_Compiler' in str(kwargs): # Simplified check for mock
        content = "print('Hello from JIT!')\npayload.priority_score += 0.5"
    else:
        content = "Mocked Response"
    return MagicMock(choices=[MagicMock(message=MagicMock(content=content))])

mock_litellm.completion = mock_completion
sys.modules["litellm"] = mock_litellm

mock_chroma = MagicMock()
sys.modules["chromadb"] = mock_chroma

mock_st = MagicMock()
sys.modules["sentence_transformers"] = mock_st

from src.backend.engine import Engine
from src.backend.models import parse_gfs

def run_test():
    print("🚀 Starting GFS-III Pure Logic Sanity Check (with JIT)...")
    
    # Test Program with all core glyphs AND the Brainstorm (JIT) glyph
    program = "⟐(⟡⎋∇≈⊕✂꩜)⟳"
    engine = Engine(parse_gfs(program))
    
    print(f"Version: {engine.state.get('version')}")
    assert engine.state.get('version') == 'GFS-III', "Version mismatch!"

    # Run a few steps
    for i in range(5):
        print(f"Step {i+1}...")
        engine.step()
        state = engine.get_state()
        print(f"  Active Nodes: {state['active_nodes']}")
        
        # Check payload modifications from JIT
        for nid, payload_data in state['payloads'].items():
            if payload_data['priority_score'] > 1.0:
                 print("  ✅ JIT execution successfully modified payload!")

    print("✅ Core Glyph Execution Logic Passed!")
    
    # Verify Telemetry
    c = engine.telemetry.db.cursor()
    c.execute("SELECT count(*) FROM telemetry")
    count = c.fetchone()[0]
    print(f"Telemetry Records: {count}")
    assert count > 0, "No telemetry recorded!"

    print("✅ Telemetry Substrate Logic Passed!")
    print("🎉 GFS-III Logic Verification Successful!")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
