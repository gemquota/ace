import { DNA_META, DNA_RANGES, HELP_DB } from './constants';

let currentSpeciesIdx = 0;
let helpMode = false;
const narrativeHistory = [];

class HelpPanel {
    constructor() {
        this.el = document.getElementById('help-panel');
        this.state = { activeKey: null, level: 2 };
    }
    open(key, level = 2) {
        this.state.activeKey = key;
        this.state.level = level;
        this.render();
        this.el.classList.remove('hidden');
    }
    close() { this.el.classList.add('hidden'); }
    render() {
        const data = HELP_DB[this.state.activeKey];
        if (!data) return;
        const layers = [
            { title: 'HINT', content: data.layers.hint },
            { title: 'EXPLANATION', content: data.layers.explanation },
            { title: 'SYSTEM', content: data.layers.system },
            { title: 'ADVANCED', content: data.layers.advanced }
        ];
        let html = `<div class="help-header"><span style="color:var(--warn); font-weight:bold;">${this.state.activeKey}</span><span class="help-close" onclick="window.closeHelp()">[X]</span></div>`;
        layers.slice(0, this.state.level).forEach(layer => {
            html += `<div class="help-layer"><div class="help-layer-title">${layer.title}</div><div class="help-layer-content">${layer.content}</div></div>`;
        });
        if (this.state.level >= 3) {
            html += `<div class="help-thresholds"><div class="help-layer-title">THRESHOLDS</div><div>Low: ${data.thresholds.low}</div><div>High: ${data.thresholds.high}</div><div>Extreme: ${data.thresholds.extreme}</div></div>`;
        }
        this.el.innerHTML = html;
    }
}

class Tooltip {
    constructor() {
        this.el = document.getElementById('tooltip');
    }
    show(key, x, y) {
        const data = HELP_DB[key];
        if (!data) return;
        this.el.innerHTML = `
            <div style="font-weight:bold; color:var(--warn); margin-bottom:5px;">${key}</div>
            <div style="font-size: 9px; line-height:1.2;">${data.layers.explanation}</div>
            <button class="tooltip-btn" onclick="window.openHelp('${key}'); window.hideTooltip();">FULL ENCYCLOPEDIA</button>
        `;
        // Constrain to screen
        const tx = Math.max(10, Math.min(window.innerWidth - 170, x - 80));
        const ty = Math.max(10, Math.min(window.innerHeight - 200, y - 120));
        
        this.el.style.left = tx + 'px';
        this.el.style.top = ty + 'px';
        this.el.classList.remove('hidden');
    }
    hide() { this.el.classList.add('hidden'); }
}

const helpPanel = new HelpPanel();
const tooltip = new Tooltip();

export function setupUI(engine) {
    window.triggerSmartChaos = () => engine.triggerSmartChaos();
    window.togglePause = () => engine.togglePause();
    window.restartSim = () => engine.restartSim();
    window.toggleLaw = (k) => engine.toggleLaw(k);
    window.updateDNA = (sIdx, rIdx, val, dId) => engine.updateDNA(sIdx, rIdx, val, dId);
    window.updateWorld = (key, val, dId) => engine.updateWorld(key, val, dId);
    window.updatePhysics = (key, val, dId) => engine.updatePhysics(key, val, dId);
    window.openTab = (event, tabId) => {
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tab-link').forEach(l => l.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        if (event) event.currentTarget.classList.add('active');
        if (tabId === 'tab-help') renderEncyclopaedia();
        if (tabId === 'tab-log') renderNarrativeLog();
    };
    window.addSpecies = () => { engine.addSpecies(); renderSpeciesList(engine); };
    window.selectSpecies = (idx) => { currentSpeciesIdx = idx; renderSpeciesList(engine); renderDNASliders(engine); };
    
    window.openHelp = (key) => helpPanel.open(key, 2);
    window.closeHelp = () => helpPanel.close();
    window.showTooltip = (key, e) => { e.stopPropagation(); tooltip.show(key, e.clientX, e.clientY); };
    window.hideTooltip = () => tooltip.hide();

    window.toggleHelpMode = () => {
        helpMode = !helpMode;
        document.getElementById('ui-layer').classList.toggle('help-mode-active', helpMode);
        document.getElementById('help-toggle').classList.toggle('active', helpMode);
        renderWorldSliders(engine);
        renderPhysicsSliders(engine);
        renderDNASliders(engine);
        if (window.renderEmergentSliders) window.renderEmergentSliders();
    };

    document.addEventListener('click', () => window.hideTooltip());

    renderWorldSliders(engine);
    renderPhysicsSliders(engine);
    renderSpeciesList(engine);
    renderDNASliders(engine);
}

function renderWorldSliders(engine) {
    const container = document.getElementById('world-sliders');
    if (!container) return;
    const items = [
        { name: 'Particle Count', key: 'count', min: 10, max: 50000, step: 10, val: engine.worldConfig.count },
        { name: 'Entropy (Grid-Chaos)', key: 'entropy', min: 0, max: 1, step: 0.05, val: engine.worldConfig.entropy },
        { name: 'Spawn Rate', key: 'spawnRate', min: 0, max: 5, step: 0.05, val: engine.worldConfig.spawnRate },
        { name: 'Shape (Cube-Sphere)', key: 'shape', min: 0, max: 1, step: 0.05, val: engine.worldConfig.shape },
        { name: 'Spread X', key: 'spreadX', min: 0.1, max: 1.0, step: 0.05, val: engine.worldConfig.spreadX },
        { name: 'Spread Y', key: 'spreadY', min: 0.1, max: 1.0, step: 0.05, val: engine.worldConfig.spreadY },
        { name: 'Spread Z', key: 'spreadZ', min: 0.1, max: 1.0, step: 0.05, val: engine.worldConfig.spreadZ },
    ];
    container.innerHTML = '<h3>World Setup</h3>';
    items.forEach(it => {
        const row = document.createElement('div');
        row.className = 'slider-row';
        const labelText = helpMode ? HELP_DB[it.name]?.layers.hint || it.name : it.name;
        row.innerHTML = `
            <span class="slider-label" onclick="window.showTooltip('${it.name}', event)">${labelText}</span>
            <div style="font-size:8px;"><span id="world-val-${it.key}">${it.val}</span></div>
            <input type="range" min="${it.min}" max="${it.max}" step="${it.step}" value="${it.val}" 
                   style="width: 100%;" oninput="window.updateWorld('${it.key}', this.value, 'world-val-${it.key}')">
        `;
        container.appendChild(row);
    });
}

function renderPhysicsSliders(engine) {
    const container = document.getElementById('phys-sliders');
    if (!container) return;
    const items = [
        { name: 'Global G', key: 'G', min: 0, max: 2, step: 0.05, val: engine.laws.G, type: 'phys' },
        { name: 'Sim Speed', key: 'dt', min: 0, max: 5, step: 0.1, val: engine.laws.dt, type: 'phys' },
        { name: 'Base Size', key: 'baseSize', min: 0.01, max: 0.5, step: 0.01, val: engine.worldConfig.baseSize, type: 'world' },
        { name: 'Map Width (X)', key: 'dimX', min: 100, max: 50000, step: 100, val: engine.worldConfig.dimX, type: 'world' },
        { name: 'Map Height (Y)', key: 'dimY', min: 100, max: 50000, step: 100, val: engine.worldConfig.dimY, type: 'world' },
        { name: 'Map Depth (Z)', key: 'dimZ', min: 100, max: 50000, step: 100, val: engine.worldConfig.dimZ, type: 'world' }
    ];
    container.innerHTML = '<h3>Simulation Scale</h3>';
    items.forEach(it => {
        const row = document.createElement('div');
        row.className = 'slider-row';
        const updateFn = it.type === 'phys' ? 'updatePhysics' : 'updateWorld';
        const labelText = helpMode ? HELP_DB[it.name]?.layers.hint || it.name : it.name;
        row.innerHTML = `
            <span class="slider-label" onclick="window.showTooltip('${it.name}', event)">${labelText}</span>
            <div style="font-size:8px;"><span id="phys-val-${it.key}">${it.val}</span></div>
            <input type="range" min="${it.min}" max="${it.max}" step="${it.step}" value="${it.val}" 
                   style="width: 100%;" oninput="window.${updateFn}('${it.key}', this.value, 'phys-val-${it.key}')">
        `;
        container.appendChild(row);
    });
}

function renderSpeciesList(engine) {
    const list = document.getElementById('species-list');
    if (!list) return;
    list.innerHTML = '';
    engine.species.forEach((s, idx) => {
        const div = document.createElement('div');
        div.className = `species-card ${idx === currentSpeciesIdx ? 'active' : ''}`;
        div.innerHTML = `<span>${s.name}</span> <div style="width:10px; height:10px; background:${s.color}"></div>`;
        div.onclick = () => window.selectSpecies(idx);
        list.appendChild(div);
    });
}

function renderDNASliders(engine) {
    const container = document.getElementById('dna-sliders');
    if (!container) return;
    const spec = engine.species[currentSpeciesIdx];
    container.innerHTML = `<h3>${spec.name} DNA</h3>`;
    DNA_META.forEach((name, idx) => {
        const val = spec.dna[idx];
        const row = document.createElement('div');
        row.className = 'slider-row';
        const labelText = helpMode ? HELP_DB[name]?.layers.hint || name : name;
        
        const label = document.createElement('span');
        label.className = 'slider-label';
        label.innerText = labelText;
        label.onclick = (e) => window.showTooltip(name, e);
        
        row.appendChild(label);
        const valDiv = document.createElement('div');
        valDiv.style.fontSize = '8px';
        const valSpan = document.createElement('span');
        valSpan.id = `dna-val-${idx}`;
        valSpan.innerText = val.toFixed(2);
        valDiv.appendChild(valSpan);
        row.appendChild(valDiv);
        
        const input = document.createElement('input');
        input.type = 'range';
        input.min = DNA_RANGES[idx].min;
        input.max = DNA_RANGES[idx].max;
        input.step = 0.05;
        input.value = val;
        input.style.width = '100%';
        input.oninput = (e) => {
            const rounded = Math.round(e.target.value * 20) / 20;
            window.updateDNA(currentSpeciesIdx, idx, rounded, `dna-val-${idx}`);
        };
        row.appendChild(input);
        container.appendChild(row);
    });
}

function renderEncyclopaedia() {
    const container = document.getElementById('encyclopaedia');
    if (!container) return;
    container.innerHTML = '<h3>Encyclopaedia</h3>';
    Object.keys(HELP_DB).forEach(key => {
        const data = HELP_DB[key];
        const div = document.createElement('div');
        div.className = 'encyclopaedia-entry';
        div.innerHTML = '<h4>' + key + '</h4><p>' + data.layers.explanation + '</p>';
        div.onclick = () => window.openHelp(key);
        container.appendChild(div);
    });
}

function renderNarrativeLog() {
    const container = document.getElementById('narrative-log');
    if (!container) return;
    container.innerHTML = '<h3>System Log</h3>';
    narrativeHistory.slice().reverse().forEach(entry => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.innerHTML = `<span class="log-time">[${entry.time}]</span> <span>${entry.text}</span>`;
        container.appendChild(div);
    });
}

export function updateHUD(fps, pCount) {
    const fpsEl = document.getElementById('fps'), pCountEl = document.getElementById('p-count');
    if (fpsEl) fpsEl.innerText = fps; if (pCountEl) pCountEl.innerText = pCount;
}

export function syncUI(laws) {
    Object.keys(laws).forEach(k => {
        const el = document.getElementById(`syn-${k}`);
        if(el) el.classList.toggle('active', laws[k]);
    });
}

export function renderInsights(insights) {
    const el = document.getElementById('insight-panel');
    if (!el) return;
    el.innerHTML = insights.map(i => `
        <div class="insight ${i.type}">
            <strong>${i.type.toUpperCase()}</strong>
            ${i.message}
        </div>
    `).join('');
}

export function renderSuggestions(suggestions) {
    const el = document.getElementById('suggestions-panel');
    if (!el) return;
    el.innerHTML = suggestions.map(s => `
        <div class="suggestion-card">
            <h4>${s.label}</h4>
            <p>${s.reason}</p>
            <button class="suggestion-btn" onclick='window.applySuggestion(${JSON.stringify(s.action)})'>APPLY</button>
        </div>
    `).join('');
}

window.applySuggestion = (action) => {
    if (action.type === 'law') {
        const current = window.engine.laws[action.key];
        window.engine.updatePhysics(action.key, current + action.delta);
    } else if (action.type === 'dna') {
        const dnaIdx = DNA_META.indexOf(action.key);
        if (dnaIdx !== -1) {
            window.engine.species.forEach((s, sIdx) => {
                const current = s.dna[dnaIdx];
                window.engine.updateDNA(sIdx, dnaIdx, current + action.delta);
            });
        }
    }
    window.selectSpecies(currentSpeciesIdx); 
};

export function renderNarrative(text) {
    const el = document.getElementById('narrative-panel');
    if (!el) return;
    el.innerText = text;
    el.classList.remove('fading');
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (narrativeHistory.length === 0 || narrativeHistory[narrativeHistory.length-1].text !== text) {
        narrativeHistory.push({ time, text });
        if (narrativeHistory.length > 100) narrativeHistory.shift();
    }
    if (window._narrativeTimer) clearTimeout(window._narrativeTimer);
    window._narrativeTimer = setTimeout(() => el.classList.add('fading'), 4000);
}

export function updateTimelineUI(max) {
    const slider = document.getElementById('timeline-slider');
    if (!slider) return;
    slider.max = max;
    if (slider.value == max - 1 || max == 1) {
        slider.value = max;
        document.getElementById('timeline-label').innerText = 'LIVE';
    }
}

window.onTimelineScrub = (e) => {
    const val = parseInt(e.target.value);
    const max = parseInt(e.target.max);
    const label = document.getElementById('timeline-label');
    if (val === max) {
        label.innerText = 'LIVE';
    } else {
        label.innerText = 'REPLAY: ' + val;
        window.engine.timelineEngine.restore(val);
    }
};

setTimeout(() => {
    const slider = document.getElementById('timeline-slider');
    if (slider) slider.oninput = window.onTimelineScrub;
}, 100);

export function notifyNewProposal(name) {
    const el = document.getElementById('proposal-panel');
    const p = window.engine.emergentEngine.pending[0];
    if (!p) return;
    el.innerHTML = `
        <h3>NEW LAW DETECTED</h3>
        <p><strong>${p.name}</strong></p>
        <p style="font-size: 8px;">${p.def.description}</p>
        <div class="proposal-actions">
            <button class="accept" onclick="window.acceptParam('${p.key}')">ACCEPT</button>
            <button class="reject" onclick="window.rejectParam('${p.key}')">REJECT</button>
        </div>
    `;
    el.classList.remove('hidden');
}

window.acceptParam = (key) => {
    const p = window.engine.emergentEngine.pending.find(x => x.key === key);
    if (p) {
        window.engine.emergentEngine.spawnAcceptedParam(p);
        window.engine.emergentEngine.pending = window.engine.emergentEngine.pending.filter(x => x.key !== key);
        renderNarrative('New law accepted: ' + p.name);
    }
    document.getElementById('proposal-panel').classList.add('hidden');
};

window.rejectParam = (key) => {
    window.engine.emergentEngine.rejected.add(key);
    window.engine.emergentEngine.pending = window.engine.emergentEngine.pending.filter(x => x.key !== key);
    document.getElementById('proposal-panel').classList.add('hidden');
};

export function renderEmergentSliders() {
    const specTab = document.getElementById('tab-spec');
    let container = document.getElementById('emergent-sliders');
    if (!container) {
        container = document.createElement('div');
        container.id = 'emergent-sliders';
        container.className = 'emergent-section';
        specTab.appendChild(container);
    }
    container.innerHTML = '<h4>Emergent Laws</h4>';
    Object.entries(window.engine.emergentEngine.metaParams).forEach(([key, val]) => {
        const row = document.createElement('div');
        row.className = 'slider-row';
        const displayName = key.replace(/_/g, ' ');
        const labelText = helpMode ? HELP_DB[displayName]?.layers.hint || displayName : displayName;
        row.innerHTML = `
            <span class="slider-label" onclick="window.showTooltip('${displayName}', event)">${labelText}</span>
            <div style="font-size:8px;"><span id="meta-val-${key}">${val.toFixed(2)}</span></div>
            <input type="range" min="0" max="1" step="0.01" value="${val}" 
                   style="width: 100%;" oninput="window.updateMetaParam('${key}', this.value)">
        `;
        container.appendChild(row);
    });
}

window.updateMetaParam = (key, val) => {
    window.engine.emergentEngine.metaParams[key] = parseFloat(val);
    document.getElementById(`meta-val-${key}`).innerText = val;
};
