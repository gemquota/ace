import litellm
import traceback
import sys
import io

class CognitiveSubstrate:
    def __init__(self, engine):
        self.engine = engine
        self.jit = JITCompiler(self)

    def call(self, messages, tier, role):
        model = "gemini/gemini-1.5-flash" if tier == 1 else "gemini/gemini-1.5-pro-latest"
        temp = 1.2 if role == "Explorer" else 0.2
        try:
            return litellm.completion(model=model, messages=messages, temperature=temp).choices[0].message.content.strip()
        except Exception:
            return "[COGNITIVE FAULT]"

class JITCompiler:
    def __init__(self, cognitive_substrate):
        self.cog = cognitive_substrate

    def compile_and_run(self, payload, graph):
        # 1. Ask LLM for Python code based on context
        context_str = "\n".join(payload.context_window[-3:])
        prompt = f"Given context:\n{context_str}\nWrite a Python script that mutates the `payload` or `graph`. ONLY return the python code, no markdown blocks."
        
        # In a real run, this would be a Tier 2 call. 
        # For mock/safety, we assume the LLM returns executable python.
        code_str = self.cog.call([{"role": "user", "content": prompt}], tier=2, role="JIT_Compiler")
        
        # Clean up markdown if LLM disobeyed
        if code_str.startswith("```python"):
            code_str = code_str.split("\n", 1)[1]
        if code_str.endswith("```"):
            code_str = code_str.rsplit("\n", 1)[0]
            
        # 2. Setup execution environment (God Mode)
        exec_globals = {
            "__builtins__": __builtins__,
            "payload": payload,
            "graph": graph,
            "Engine": self.cog.engine
        }
        
        # 3. Execute and capture stdout/tracebacks
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        
        try:
            exec(code_str, exec_globals)
            output = redirected_output.getvalue()
            if output:
                payload.context_window.append(f"[JIT_OUTPUT]: {output.strip()}")
            payload.entropy_index += 0.5 # Execution increases entropy
        except Exception as e:
            tb = traceback.format_exc()
            payload.context_window.append(f"[JIT_FAULT]: {tb}")
            payload.entropy_index += 2.0 # Faults massively spike entropy
        finally:
            sys.stdout = old_stdout
