```python
import os
import re
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# ==========================================
# 1. THE RRP MASTER SYSTEM PROMPT (UPDATED & EXPANDED)
# ==========================================
RRP_MASTER_PROMPT = """
Act as the Lead Architect and Facilitator for the Recursive Refinement Protocol (RRP). Your core objective is to act as a buffer between a raw idea and actual code. You will systematically break down, refine, and lock in the user's intent through a highly structured, variable-driven Q&A process. Stop us from jumping into execution too early by forcing clarity first.

Core Variables:
- U: Use Case (The focus of our session, which changes how you ask questions and what you output).
- M: Execution Mode (How we handle the back-and-forth pacing).
- X: Number of open-ended questions per round.
- Y: Number of multiple-choice questions (MCQs) PER open-ended question.
- Z: Number of total rounds.

1) Initialization & Auto-Selection:
The user might give you exact numbers (e.g., U=3, M=1, X=2, Y=3, Z=3) or simply say "AUTO". 
- If they say "AUTO" or leave the variables out entirely, you need to read the room. Look at their initial prompt, gauge the complexity, and autonomously pick the best (U, M, X, Y, Z) configuration to get the job done.
- Before you ask a single question, your very first response MUST explicitly confirm the variables you are using, the Use Case we are tackling, and how the turn-by-turn pacing will work.

2) Global Behavior (The Rolling Summary):
No matter what Use Case or Mode we are in, you must maintain a `[Rolling Project Summary]` block that concisely paraphrases everything we have agreed on so far, constantly upgrading the master narrative so we never lose context.
- For M=1 and M=2: Output the updated summary at the beginning of every Round, right below your state tracker.
- For M=3 (Quiz Show): Do NOT print the summary during the rapid-fire Q&A loop. Update it silently in your own context window to guide your questions, but keep the terminal output clean. Only print the full summary at the very end of the session, right before generating the final documents.

3) Use Case Matrix (U):
- [U=1] General Clarity & Alignment: Your Mindset: The Objective Facilitator. Logic: Broadly eliminate ambiguity, vague nouns, and assumptions. Ask exactly X open questions, followed by Y MCQs per open question. Outputs: `synthesis_document.md`, `decision_log.md`.
- [U=2] Divergent Brainstorming & Ideation: Your Mindset: The Provocateur. Logic: Expansive, lateral thinking. Override Y to 0 (No MCQs). Maximize X for "What if?" questions to push boundaries. Outputs: `ideation_matrix.md`, `concept_map.mmd`.
- [U=3] Convergent Decision Making & Narrowing: Your Mindset: The Reductionist. Logic: Force hard technical commitments. Override X to 1. Maximize Y to provide an exhaustive, mutually exclusive list of highly specific technical paths. Outputs: `concrete_spec.md`, `binary_decision_tree.mmd`.
- [U=4] Multi-Perspective Stress Testing: Your Mindset: The Red Team. Logic: Ask 1 open-ended question. Invent distinct perspectives (e.g., Hacker, End-user, Server spike). Ask Y MCQs from the perspective of those personas. Outputs: `stress_test_report.md`, `risk_mitigation_matrix.md`.
- [U=5] Data, Logic & Relationship Mapping: Your Mindset: The Database Architect. Logic: Focus strictly on relationships, boundaries, and state transitions. MCQs force definitions of data types and logic gates. Outputs: `taxonomy_and_schemas.md`, `entity_relationship_model.mmd`.
- [U=6] Feature Specification & Deterministic Engine Architecture: Your Mindset: The Systems Engineer. Logic: Edge cases, logic gates, UI/UX dependencies. Open questions demand algorithmic steps. MCQs focus entirely on error-handling and failure states. Outputs: `technical_spec.md`, `state_flow.mmd`, `atomic_task_list.md`.

4) Pacing Modes (M) - Strict State Machines:
You must strictly follow these rules for pausing and waiting. Never talk over the user or answer your own questions. Stop at every [MANDATORY PAUSE].
- [M=1: The Hybrid Pipeline] Loop: Output Summary. Ask X open questions. [MANDATORY PAUSE]. Wait for answers. Ask Y MCQs + next batch of X open questions. [MANDATORY PAUSE]. Final: Output required documents.
- [M=2: The Offline Batch] Step 1: Output Summary. Generate ALL open questions upfront inside `rrp_open.md`. [MANDATORY PAUSE]. Step 2: Receive answers. Generate ALL corresponding MCQs inside `rrp_mcq.md`. [MANDATORY PAUSE]. Final: Receive MCQ choices. Output required documents.
- [M=3: The Rapid-Fire Quiz Show] Loop: (Silent Summary Update). Ask exactly ONE open-ended question. [MANDATORY PAUSE]. Wait for answer. Ask Y MCQs directly related to that specific answer. [MANDATORY PAUSE]. Repeat until round limit is hit. Final: Output required documents.

5) Protocol Rules:
- The Context Anchor: To prevent context drift during long sessions, you must start EVERY single response with a strict, 1-line Anchor block. Do not skip this. Format: `[RRP | U={U} | M={M} | Rnd {n}/{Z} | Pending: {X} Open, {Y} MCQ | Goal: {1-sentence summary of the Use Case logic}]`
- No Coding Allowed: Do not write functional target code (Python, JS, etc.) during the Q&A phase. Focus purely on logic extraction and strategy.
- Terminal Trigger: The moment the required rounds are complete, stop asking questions and immediately output the final document set.
"""

# ==========================================
# 2. FASTAPI MICRO-SERVER & STATE
# ==========================================
app = FastAPI()

# In-memory state for Context Pruning
class RRPState:
    def __init__(self):
        self.history = [] # Stores last N turns
        self.rolling_summary = "No summary generated yet."
        self.max_history_turns = 4 # Prune history beyond this

state = RRPState()

class ChatRequest(BaseModel):
    message: str

def clean_ansi(text: str) -> str:
    """Strips hidden ANSI escape codes scraped from terminal stdout."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def build_stateless_payload(user_message: str) -> str:
    """Builds the perfectly pruned context payload."""
    payload = f"SYSTEM INSTRUCTIONS:\n{RRP_MASTER_PROMPT}\n\n"
    payload += f"CURRENT ROLLING SUMMARY:\n{state.rolling_summary}\n\n"
    payload += "RECENT HISTORY:\n"
    for turn in state.history:
        payload += f"{turn}\n"
    payload += f"\nUSER NEW MESSAGE:\n{user_message}\n"
    return payload

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 1. Build stateless payload
    payload = build_stateless_payload(req.message)
    
    # Write to a temp file to avoid quoting issues in shell
    temp_file = "rrp_temp_payload.txt"
    with open(temp_file, "w") as f:
        f.write(payload)
        
    try:
        # 2. Subprocess Handoff to Gemini CLI
        cmd = f'cat {temp_file} | gemini generate-content'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        raw_output = result.stdout
        
        # 3. Clean and Extract
        clean_output = clean_ansi(raw_output).strip()
        if not clean_output:
            clean_output = "Error: CLI returned empty response. Check CLI connection."
        
        # 4. Context Pruning Maintenance
        state.history.append(f"User: {req.message}")
        state.history.append(f"AI: {clean_output}")
        
        # Prune if too long (Keep token count flat)
        if len(state.history) > state.max_history_turns * 2:
            state.history = state.history[-(state.max_history_turns * 2):]
            
        # Optional: Extract summary if printed in the output to save to state
        if "[Rolling Project Summary]" in clean_output:
            parts = clean_output.split("[Rolling Project Summary]")
            if len(parts) > 1:
                extracted = parts[1].split("\n\n")[0].strip()
                state.rolling_summary = extracted
                
    except Exception as e:
        clean_output = f"Python Execution Error: {str(e)}"
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return {"response": clean_output}

@app.post("/execute")
async def execute_artifacts():
    """Triggered by 'Generate Blueprint' button. Writes files."""
    return {"status": "Execution hook hit. Integrate with `gemini chat` or `aider` CLI here."}

# ==========================================
# 3. EMBEDDED HTML FRONTEND
# ==========================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RRP Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });
        window.mermaid = mermaid;
    </script>
    <style>
        body { background-color: #0f172a; color: #cbd5e1; }
        .chat-ai { border-left: 4px solid #3b82f6; background-color: #1e293b; padding: 1rem; margin-bottom: 1rem; border-radius: 0 0.5rem 0.5rem 0;}
        .chat-user { border-left: 4px solid #10b981; background-color: #0f172a; padding: 1rem; margin-bottom: 1rem; border-radius: 0 0.5rem 0.5rem 0;}
        pre { background: #000; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-top: 0.5rem; }
        code { font-family: monospace; color: #38bdf8; }
    </style>
</head>
<body class="h-screen flex flex-col overflow-hidden">

    <!-- Top Bar -->
    <header class="bg-slate-900 border-b border-slate-700 p-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-white tracking-widest">RRP <span class="text-blue-500">ENGINE</span></h1>
        <div id="status-anchor" class="text-xs md:text-sm font-mono text-yellow-400 truncate ml-4">[RRP | Waiting for Initialization]</div>
    </header>

    <!-- Main Layout -->
    <div class="flex-1 flex overflow-hidden">
        <!-- Chat Feed -->
        <main class="flex-1 overflow-y-auto p-4 md:p-6" id="chat-feed">
            <div class="text-center text-slate-500 mt-10">
                Initialize session (e.g. "AUTO" or "U=3, M=3, X=1, Y=3, Z=5")
            </div>
        </main>
    </div>

    <!-- Input Footer -->
    <footer class="bg-slate-800 border-t border-slate-700 p-4">
        <div class="max-w-4xl mx-auto flex gap-2 md:gap-4" id="input-container">
            <textarea id="user-input" rows="2" class="flex-1 bg-slate-900 border border-slate-600 rounded p-3 text-white focus:outline-none focus:border-blue-500" placeholder="Type your answer or initialization variables..."></textarea>
            <button onclick="sendMessage()" id="send-btn" class="bg-blue-600 hover:bg-blue-500 text-white px-4 md:px-6 rounded font-bold transition-colors">SEND</button>
        </div>
        
        <div class="max-w-4xl mx-auto mt-3 flex justify-between text-xs text-slate-400">
            <span>Powered by Gemini CLI + Python Context Pruner</span>
            <button onclick="executeArtifacts()" class="text-green-400 hover:text-green-300 font-bold border border-green-500 px-2 py-1 rounded">Generate Blueprint</button>
        </div>
    </footer>

    <script>
        const chatFeed = document.getElementById('chat-feed');
        const inputField = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const statusAnchor = document.getElementById('status-anchor');

        // Handle Enter to send (Shift+Enter for new line)
        inputField.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        async function sendMessage(textOverride = null) {
            const text = textOverride || inputField.value.trim();
            if (!text) return;

            // Render User Message
            inputField.value = '';
            appendMessage('user', text);
            scrollToBottom();

            // Loading UI
            sendBtn.innerText = 'WAIT';
            sendBtn.disabled = true;
            inputField.disabled = true;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                
                const data = await response.json();
                processAiResponse(data.response);

            } catch (error) {
                appendMessage('ai', 'Error connecting to Python backend. Is the server running?');
            } finally {
                sendBtn.innerText = 'SEND';
                sendBtn.disabled = false;
                inputField.disabled = false;
                inputField.focus();
            }
        }

        async function processAiResponse(rawText) {
            // 1. Extract and update the Status Anchor
            const anchorMatch = rawText.match(/\\[RRP.*?\\]/);
            if (anchorMatch) {
                statusAnchor.innerText = anchorMatch[0];
                rawText = rawText.replace(anchorMatch[0], '').trim(); 
            }

            // 2. Render Markdown
            let htmlContent = marked.parse(rawText);
            const msgDiv = appendMessage('ai', '');
            msgDiv.innerHTML = htmlContent;

            // 3. Render Mermaid Diagrams natively in browser
            const mermaidBlocks = msgDiv.querySelectorAll('code.language-mermaid');
            for (let i = 0; i < mermaidBlocks.length; i++) {
                const block = mermaidBlocks[i];
                const graphDef = block.textContent;
                const id = `mermaid-${Date.now()}-${i}`;
                const preNode = block.parentNode;
                preNode.outerHTML = `<div class="mermaid" id="${id}">${graphDef}</div>`;
                await window.mermaid.run({ querySelector: `#${id}` });
            }
            
            scrollToBottom();
        }

        function appendMessage(role, rawContent) {
            const div = document.createElement('div');
            div.className = role === 'ai' ? 'chat-ai' : 'chat-user';
            
            if (role === 'user') {
                div.innerText = rawContent;
            } else {
                div.innerHTML = rawContent; // Assumes pre-parsed HTML for AI
            }
            
            // Remove the initial placeholder if present
            if (chatFeed.children.length === 1 && chatFeed.children[0].classList.contains('text-center')) {
                chatFeed.innerHTML = '';
            }
            
            chatFeed.appendChild(div);
            return div;
        }

        function scrollToBottom() {
            chatFeed.scrollTop = chatFeed.scrollHeight;
        }

        async function executeArtifacts() {
            const response = await fetch('/execute', { method: 'POST' });
            const data = await response.json();
            alert(data.status);
        }
    </script>
</body>
</html>

```
