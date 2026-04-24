import os
import re
import json

# Use absolute paths to avoid confusion
BASE_DIR = '/data/data/com.termux/files/home/dev/cap'
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
ONTOLOGY_DIR = os.path.join(DOCS_DIR, 'system_ontology')
OUTPUT_DIR = os.path.join(DOCS_DIR, 'compiled')
MD_OUTPUT = os.path.join(OUTPUT_DIR, 'CAP_PHASE20_FULL_SPEC.md')

# Fork 1: Machinery Sanguine (The High-Fidelity UI)
MACHINERY_HTML = os.path.join(OUTPUT_DIR, 'compiled.html')

# Fork 2: Grid Spec (The Experimental Accordion Grid)
GRID_HTML = os.path.join(OUTPUT_DIR, 'grid_spec.html')

ORDER = [
    "architecture.md", "directory-structure.md", "v3-migration.md", "ontology.md",
    "kernel.md", "healer-rollback.md", "apc-runtime.md", "execution-model.md",
    "worker-queue.md", "pie.md", "clide.md", "memory.md", "sovereign.md",
    "meta-cognition.md", "swarm-economy.md", "openworld-mcp.md", "dashboard.md",
    "ui-engine.md", "orchestration.md", "schema.md", "scripts.md", "build-system.md",
    "autopoietic-history.md", "usage.md", "testing.md", "security.md", "performance.md",
    "ui-evolution.md", "glossary.md", "final_report.md"
]

def get_ontology_files():
    if not os.path.exists(ONTOLOGY_DIR): return []
    return sorted([f for f in os.listdir(ONTOLOGY_DIR) if f.endswith('.md')])

def generate_markdown():
    full_content = "# 🛡️ CAP.OS // PHASE 20 COMPLETE FORENSIC CORPUS\n\n## 📖 TABLE OF CONTENTS\n\n"
    for i, filename in enumerate(ORDER, 1):
        title = filename.replace(".md", "").replace("-", " ").upper()
        full_content += f"{i}. [{title}](#{filename.replace('.md', '')})\n"
    full_content += "\n### 🧬 SYSTEM ONTOLOGY\n\n"
    ontology_files = get_ontology_files()
    for i, filename in enumerate(ontology_files, 1):
        title = filename.replace(".md", "").replace("_", "/").upper()
        full_content += f"{i}. [{title}](#ontology_{filename.replace('.', '_')})\n"
    full_content += "\n---\n\n"
    for filename in ORDER:
        path = os.path.join(DOCS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                full_content += f"<a name=\"{filename.replace('.md', '')}\"></a>\n\n{f.read()}\n\n---\n\n"
    full_content += "\n# 🧬 SYSTEM ONTOLOGY RECORDS\n\n"
    for filename in ontology_files:
        path = os.path.join(ONTOLOGY_DIR, filename)
        with open(path, 'r') as f:
            full_content += f"<a name=\"ontology_{filename.replace('.', '_')}\"></a>\n\n## {filename.upper()}\n\n{f.read()}\n\n---\n\n"
    with open(MD_OUTPUT, 'w') as f: f.write(full_content)

def generate_machinery_html(docs_data):
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAP SANGUINE // MACHINERY_SPEC</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg-deep: #050505;
            --red-muted: #441010;
            --red-mid: #661a1a;
            --red-bright: #aa2424;
            --cyan-dim: #10404a;
            --border-muted: rgba(80, 20, 20, 0.3);
            --metal-shine: linear-gradient(135deg, #1a1a1a 0%, #111 45%, #222 50%, #111 55%, #0a0a0a 100%);
            --trans-timing: 0.8s cubic-bezier(0.19, 1, 0.22, 1);
        }

        body, html {
            margin: 0; padding: 0; height: 100%;
            background-color: var(--bg-deep); color: #777;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            overflow: hidden; 
        }

        /* PERFORMANCE */
        * { box-sizing: border-box; }
        .menu-chunk { will-change: transform, opacity; }
        
        .bg-lines {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: linear-gradient(var(--border-muted) 1px, transparent 1px),
                              linear-gradient(90deg, var(--border-muted) 1px, transparent 1px);
            background-size: 80px 80px; opacity: 0.03; z-index: 0;
        }

        #app-container { position: relative; width: 100vw; height: 100vh; z-index: 10; }
        #content-wrapper { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; overflow-y: auto; background: #000; z-index: 1; }
        #content { padding: 80px 100px; max-width: 1000px; margin: 0 auto; min-height: 100%; background: #050505; }

        /* OVERLAY WRAPPER */
        #sidebar-overlay { position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 100; pointer-events: none; perspective: 1500px; }
        #sidebar-overlay.active { pointer-events: auto; }
        #sidebar-scroll-area { 
            width: 460px; height: 100%; padding: 60px 40px 60px 80px; box-sizing: border-box; 
            overflow-y: auto; overflow-x: visible; pointer-events: auto; scrollbar-width: none; position: relative;
        }
        #sidebar-scroll-area::-webkit-scrollbar { display: none; }

        /* TECHNO-CENTIPEDE */
        #centipede-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; }
        .spine-path { fill: none; stroke: var(--red-muted); stroke-width: 4; stroke-dasharray: 12 6; opacity: 0.3; }
        .vertebrae { fill: #000; stroke: var(--red-mid); stroke-width: 2; }
        .nerve-line { stroke: var(--red-muted); stroke-width: 1; opacity: 0.2; }

        /* CHUNKS - CATEGORY MODALS */
        .menu-chunk {
            background: var(--metal-shine); border: 1px solid #1a1a1a;
            box-shadow: 15px 15px 35px rgba(0,0,0,0.9);
            margin-bottom: 50px; position: relative;
            transform-origin: left center; transform-style: preserve-3d;
            transition: transform var(--trans-timing), opacity 0.5s ease;
            z-index: 10;
        }
        .chunk-inner {
            margin: 6px; background: rgba(12, 12, 12, 0.9); border: 1px solid rgba(255, 255, 255, 0.02);
            padding: 25px; position: relative; z-index: 2;
        }
        .bolt { position: absolute; width: 6px; height: 6px; background: #222; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        .t-l { top: 6px; left: 6px; } .t-r { top: 6px; right: 6px; } .b-l { bottom: 6px; left: 6px; } .b-r { bottom: 6px; right: 6px; }

        /* DEPLOY ANIMATION */
        #sidebar-overlay:not(.active) .menu-chunk { opacity: 0; pointer-events: none; }
        #sidebar-overlay:not(.active) .chunk-type-1 { transform: rotateY(-100deg) translateX(-100px) translateZ(-500px); }
        #sidebar-overlay:not(.active) .chunk-type-2 { transform: rotateY(-120deg) translateX(-200px) translateZ(-700px); }
        #sidebar-overlay:not(.active) .chunk-type-3 { transform: rotateY(-80deg) translateX(-50px) translateZ(-400px); }
        #sidebar-overlay:not(.active) .chunk-type-4 { transform: rotateX(80deg) translateY(-200px) translateZ(-600px); }

        .brand { font-size: 0.8em; font-weight: bold; color: #fff; text-align: center; letter-spacing: 4px; padding-bottom: 12px; margin-bottom: 5px; border-bottom: 1px solid var(--red-muted); text-transform: uppercase; }
        .tier-1-header { color: var(--red-bright); font-size: 0.7em; text-transform: uppercase; letter-spacing: 3px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.03); margin-bottom: 12px; }

        /* SUB-CATEGORIES - ACCORDIONS */
        .tier-2-wrapper { margin-bottom: 10px; }
        .tier-2-header {
            color: #bbb; font-size: 0.65em; text-transform: uppercase; letter-spacing: 2px;
            padding: 12px 15px; background: rgba(5,5,5,0.6); border-left: 3px solid var(--red-muted);
            cursor: pointer; display: flex; justify-content: space-between; align-items: center;
            transition: all 0.3s;
        }
        .tier-2-header:hover { color: #fff; background: rgba(100, 20, 20, 0.1); }
        .tier-2-header::after { content: '◈'; font-size: 0.8em; color: #444; transition: transform 0.6s; }
        .tier-2-wrapper.active .tier-2-header::after { transform: rotate(180deg); color: var(--red-bright); }

        .tier-3-container { max-height: 0; overflow: hidden; transition: max-height 0.8s cubic-bezier(0.19, 1, 0.22, 1), opacity 0.4s; opacity: 0; }
        .tier-2-wrapper.active .tier-3-container { max-height: 2000px; opacity: 1; }

        .doc-link { display: block; padding: 10px 20px; color: #555; text-decoration: none; cursor: pointer; font-size: 0.75em; transition: all 0.2s; }
        .doc-link:hover { color: #888; background: rgba(255,255,255,0.02); padding-left: 25px; }
        .doc-link.active { color: #fff; background: rgba(100, 20, 20, 0.2); border-right: 3px solid var(--red-bright); }

        #menu-trigger {
            position: fixed; top: 40px; left: 40px; z-index: 1000;
            background: #111; border: 1px solid #222; color: #444; padding: 20px 30px; cursor: pointer;
            font-size: 0.6em; text-transform: uppercase; letter-spacing: 6px; transition: all 0.4s;
        }
        #menu-trigger:hover { color: #999; border-color: #444; }
        #menu-trigger.hidden { opacity: 0; pointer-events: none; transform: translateX(-50px); }

        /* MARKDOWN */
        #content h1 { color: #eee; border-bottom: 2px solid var(--red-muted); padding-bottom: 15px; font-size: 2em; }
        #content h2 { color: var(--red-bright); font-size: 1.4em; margin-top: 40px; }
        #content p, #content li { line-height: 1.8; color: #666; font-size: 1em; }
        #content pre { background: #000; border: 1px solid #1a1a1a; padding: 20px; border-radius: 4px; overflow-x: auto; color: #888; }
    </style>
</head>
<body>
    <div class="bg-lines"></div>
    <button id="menu-trigger" onclick="toggleMenu(true)">[ DEPLOY_MACHINERY ]</button>

    <div id="app-container">
        <div id="content-wrapper"><div id="content"><h1 style="text-align:center; margin-top: 35vh; border:none; color: #111; font-size: 5em; letter-spacing: 40px;">IDLE</h1></div></div>
        <div id="sidebar-overlay" onclick="toggleMenu(false)">
            <div id="sidebar-scroll-area">
                <svg id="centipede-svg"><path class="spine-path" id="spine-path-el" d=""></path></svg>
                <div class="menu-chunk chunk-type-1" style="transition-delay: 0s;"><div class="bolt t-l"></div><div class="bolt t-r"></div><div class="bolt b-l"></div><div class="bolt b-r"></div><div class="chunk-inner"><div class="brand">MACHINERY // SANGUINE</div></div></div>
                <div id="menu-chunks"></div>
            </div>
        </div>
    </div>

    <script>
        const docsData = {{DOCS_DATA_JSON}};
        let isSidebarActive = false;

        function toggleMenu(force) {
            isSidebarActive = (force !== undefined) ? force : !isSidebarActive;
            document.getElementById('sidebar-overlay').classList.toggle('active', isSidebarActive);
            document.getElementById('menu-trigger').classList.toggle('hidden', isSidebarActive);
            if(isSidebarActive) { 
                setTimeout(updateCentipede, 100); setTimeout(updateCentipede, 400); setTimeout(updateCentipede, 900);
            }
        }

        function updateCentipede() {
            const chunks = document.querySelectorAll('.menu-chunk');
            const pathEl = document.getElementById('spine-path-el');
            const svg = document.getElementById('centipede-svg');
            if (!chunks.length) return;
            
            document.querySelectorAll('.v-node').forEach(v => v.remove());
            let pathD = "";
            const spineX = 40;

            chunks.forEach((chunk, i) => {
                const y = chunk.offsetTop + chunk.offsetHeight / 2;
                if (i === 0) pathD = `M ${spineX} ${y}`;
                else {
                    const py = chunks[i-1].offsetTop + chunks[i-1].offsetHeight/2;
                    pathD += ` C ${spineX + 20} ${py + 20}, ${spineX - 20} ${y - 20}, ${spineX} ${y}`;
                    
                    // Add legs between chunks
                    for (let step = 1; step < 4; step++) {
                        const midY = py + (y - py) * (step / 4);
                        const legLeft = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        legLeft.setAttribute("x1", spineX); legLeft.setAttribute("y1", midY);
                        legLeft.setAttribute("x2", spineX - 15); legLeft.setAttribute("y2", midY + 5);
                        legLeft.setAttribute("class", "nerve-line v-node"); svg.appendChild(legLeft);
                        
                        const legRight = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        legRight.setAttribute("x1", spineX); legRight.setAttribute("y1", midY);
                        legRight.setAttribute("x2", spineX + 15); legRight.setAttribute("y2", midY + 5);
                        legRight.setAttribute("class", "nerve-line v-node"); svg.appendChild(legRight);
                    }
                }
                
                const node = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                node.setAttribute("cx", spineX); node.setAttribute("cy", y); node.setAttribute("r", 5);
                node.setAttribute("class", "vertebrae v-node"); svg.appendChild(node);
                
                const nerve = document.createElementNS("http://www.w3.org/2000/svg", "line");
                nerve.setAttribute("x1", spineX); nerve.setAttribute("y1", y); nerve.setAttribute("x2", chunk.offsetLeft); nerve.setAttribute("y2", y);
                nerve.setAttribute("class", "nerve-line v-node"); svg.appendChild(nerve);
            });
            pathEl.setAttribute("d", pathD);
            svg.setAttribute("height", document.getElementById('sidebar-scroll-area').scrollHeight);
        }

        function renderMenu() {
            const container = document.getElementById('menu-chunks');
            Object.entries(docsData).forEach(([cat, subcats], i) => {
                const delay = (i * 0.04) + "s";
                const chunk = document.createElement('div');
                chunk.className = `menu-chunk chunk-type-${(i % 4) + 1}`;
                chunk.style.transitionDelay = delay;
                ['t-l', 't-r', 'b-l', 'b-r'].forEach(p => { const b = document.createElement('div'); b.className = `bolt ${p}`; chunk.appendChild(b); });
                const inner = document.createElement('div'); inner.className = 'chunk-inner';
                const h = document.createElement('div'); h.className = 'tier-1-header'; h.textContent = cat; inner.appendChild(h);
                
                Object.entries(subcats).forEach(([sub, files]) => {
                    const wrapper = document.createElement('div'); wrapper.className = 'tier-2-wrapper';
                    const head = document.createElement('div'); head.className = 'tier-2-header'; head.textContent = sub;
                    head.onclick = (e) => { e.stopPropagation(); wrapper.classList.toggle('active'); setTimeout(updateCentipede, 10); setTimeout(updateCentipede, 800); };
                    wrapper.appendChild(head);
                    const list = document.createElement('div'); list.className = 'tier-3-container';
                    Object.entries(files).forEach(([title, content]) => {
                        const a = document.createElement('a'); a.className = 'doc-link'; a.textContent = title;
                        a.onclick = (e) => { e.stopPropagation(); document.querySelectorAll('.doc-link').forEach(l => l.classList.remove('active')); a.classList.add('active'); renderContent(content); toggleMenu(false); };
                        list.appendChild(a);
                    });
                    wrapper.appendChild(list); inner.appendChild(wrapper);
                });
                chunk.appendChild(inner); container.appendChild(chunk);
            });
        }

        function renderContent(md) {
            const div = document.getElementById('content');
            div.style.opacity = 0;
            setTimeout(() => { div.innerHTML = marked.parse(md); div.style.opacity = 1; document.getElementById('content-wrapper').scrollTop = 0; }, 200);
        }

        document.addEventListener('DOMContentLoaded', () => {
            renderMenu();
            document.getElementById('sidebar-scroll-area').addEventListener('scroll', () => { if(isSidebarActive) requestAnimationFrame(updateCentipede); });
        });
    </script>
</body>
</html>"""
    final = template.replace("{{DOCS_DATA_JSON}}", json.dumps(docs_data))
    with open(MACHINERY_HTML, 'w') as f: f.write(final)

def generate_forks():
    machinery_data = {}
    core_chunks = {
        "I. FOUNDATIONS": ["architecture.md", "directory-structure.md", "v3-migration.md", "ontology.md"],
        "II. EXECUTION": ["kernel.md", "healer-rollback.md", "apc-runtime.md", "execution-model.md"],
        "III. COGNITION": ["pie.md", "clide.md", "memory.md", "meta-cognition.md"],
        "IV. ECOSYSTEM": ["swarm-economy.md", "openworld-mcp.md", "dashboard.md", "ui-engine.md"],
        "V. OPERATIONS": ["orchestration.md", "schema.md", "scripts.md", "build-system.md", "autopoietic-history.md"],
        "VI. PROTOCOLS": ["usage.md", "testing.md", "security.md", "performance.md", "ui-evolution.md", "glossary.md", "final_report.md"]
    }
    for chunk, files in core_chunks.items():
        machinery_data[chunk] = {}
        for f in files:
            p = os.path.join(DOCS_DIR, f)
            if os.path.exists(p):
                with open(p, 'r') as file: machinery_data[chunk][f.replace(".md", "").replace("-", " ").upper()] = file.read()
    
    ont_files = get_ontology_files()
    ont_groups = {}
    for f in ont_files:
        p = f.split('_')
        prefix = f"{p[0]}_{p[1]}" if len(p) >= 2 and p[0] == 'core' else (p[0] if '_' in f else 'OTHER')
        if prefix not in ont_groups: ont_groups[prefix] = []
        ont_groups[prefix].append(f)
    for prefix, files in sorted(ont_groups.items()):
        chunk = f"Ω. ONTOLOGY: {prefix.upper()}"
        machinery_data[chunk] = {"ALL RECORDS": {}}
        for f in sorted(files):
            with open(os.path.join(ONTOLOGY_DIR, f), 'r') as file: machinery_data[chunk]["ALL RECORDS"][f.replace(".md", "").replace("_", "/").upper()] = file.read()
    generate_machinery_html(machinery_data)

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    generate_markdown()
    generate_forks()
