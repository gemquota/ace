import { API } from './api.js';
import { Renderer } from './canvas.js';
import { Builder } from './editor.js';

class LogViewer {
    constructor() {
        this.container = document.getElementById('log-output');
        this.lastTick = -1;
    }
    update(stateData) {
        if (!stateData || !stateData.state || !this.container) return;
        const currentTick = stateData.state.tick;
        
        if (currentTick !== this.lastTick && currentTick >= 0) {
            this.lastTick = currentTick;
            if(stateData.events) {
                stateData.events.forEach(e => {
                    if(e.type === 'exec') return; 
                    const div = document.createElement('div');
                    div.className = 'log-entry';
                    div.innerHTML = `<span style="color:#fff; font-weight:bold;">[T:${currentTick}]</span> <span style="color:#f0f;">[SYS]</span> ${e.type.toUpperCase()} at ${e.node ? e.node.substring(0,6) : 'N/A'}`;
                    this.container.appendChild(div);
                });
            }
            this.container.scrollTop = this.container.scrollHeight;
        }
    }
    appendTelemetry(tel) {
        const div = document.createElement('div');
        div.className = 'log-entry telemetry-entry';
        div.innerHTML = `<span style="color:#0f0; font-weight:bold;">[T:${tel.tick}]</span> [${tel.agent_id.substring(0,6)}] ${tel.role} | Score: ${tel.score.toFixed(2)} | Ent: ${tel.entropy.toFixed(2)}`;
        this.container.appendChild(div);
        this.container.scrollTop = this.container.scrollHeight;
    }
    clear() {
        if(this.container) this.container.innerHTML = '';
        this.lastTick = -1;
    }
}

class AgentPOV {
    constructor() {
        this.container = document.getElementById('agent-pov-container');
    }
    update(payloads) {
        if (!this.container || !payloads) return;
        this.container.innerHTML = '';
        Object.keys(payloads).forEach(nid => {
            const p = payloads[nid];
            const div = document.createElement('div');
            div.className = 'pov-panel';
            const contextText = p.context_window.length ? p.context_window[p.context_window.length - 1] : "Empty";
            div.innerHTML = `
                <div class="pov-header">[${p.agent_id}] ${p.current_role}</div>
                <div class="pov-body">Node: ${nid.substring(0,6)}<br>Context: ${contextText.substring(0, 50)}...</div>
            `;
            this.container.appendChild(div);
        });
    }
}

class TimelineScrubber {
    constructor() {
        this.slider = document.getElementById('timeline-slider');
        this.display = document.getElementById('timeline-display');
        this.historyData = [];
    }
    async load() {
        try {
            const res = await fetch('/api/history');
            this.historyData = await res.json();
            if (this.slider && this.historyData.length > 0) {
                this.slider.max = this.historyData[this.historyData.length - 1].tick;
                this.slider.value = this.slider.max;
                this.updateDisplay();
            }
        } catch(e) { console.error("Failed to load history", e); }
    }
    updateDisplay() {
        if (this.display && this.slider) {
            this.display.textContent = `Historical Tick: ${this.slider.value}`;
        }
    }
}

try {
    const canvasEl = document.getElementById('canvas');
    if (!canvasEl) throw new Error("CRITICAL: <canvas id='canvas'> not found!");
    
    const renderer = new Renderer(canvasEl);
    const builder = new Builder((text) => {
        const input = document.getElementById('program-input');
        if (input) input.value = text;
    });
    const logViewer = new LogViewer();
    const agentPov = new AgentPOV();
    const timeline = new TimelineScrubber();
    
    let lastGraphState = null;

    const bind = (id, fn) => {
        const el = document.getElementById(id);
        if (el) el.onclick = fn;
    };
    const toggleDrawer = (id) => {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('open');
    };

    // UI Bindings
    bind('btn-toggle-builder', () => toggleDrawer('builder-drawer'));
    bind('btn-close-builder', () => document.getElementById('builder-drawer').classList.remove('open'));
    bind('btn-toggle-lib', () => toggleDrawer('library-drawer'));
    bind('btn-close-lib', () => document.getElementById('library-drawer').classList.remove('open'));
    bind('btn-toggle-log', () => toggleDrawer('log-drawer'));

    // Engine Controls
    bind('btn-play', API.play);
    bind('btn-pause', () => { API.pause(); ws.send(JSON.stringify({action: "pause"})); });
    bind('btn-load', () => {
        const input = document.getElementById('program-input');
        if(!input) return;
        API.pause().then(() => {
            API.loadProgram(input.value);
            renderer.nodePositions = {}; 
            logViewer.clear();
            timeline.load();
        });
    });
    bind('btn-reload', () => document.getElementById('btn-load').click());

    // Timeline binding
    const tSlider = document.getElementById('timeline-slider');
    if (tSlider) {
        tSlider.oninput = () => timeline.updateDisplay();
    }

    // GFS-III Multiplexed WebSocket
    const ws = new WebSocket(`ws://${window.location.host}/api/ws`);
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        
        if (msg.type === "state") {
            lastGraphState = msg.data;
            const view = document.getElementById('state-view');
            if(view && lastGraphState.state) {
                view.textContent = `Tick: ${lastGraphState.state.tick} | Nodes: ${lastGraphState.graph.nodes.length}`;
            }
            logViewer.update(lastGraphState);
            agentPov.update(lastGraphState.payloads);
        } else if (msg.type === "telemetry") {
            logViewer.appendTelemetry(msg.data);
        }
    };

    ws.onclose = () => {
        const view = document.getElementById('state-view');
        if(view) view.textContent = "CONNECTION LOST";
    };

    // Load initial history
    timeline.load();

    function loop() {
        if (lastGraphState) {
            renderer.updatePhysics(lastGraphState);
            renderer.draw(lastGraphState);
        }
        requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

} catch (err) {
    alert("JAVASCRIPT CRASH: " + err.message);
}
