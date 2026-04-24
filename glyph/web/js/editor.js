import { API } from './api.js';

export class Builder {
    constructor(onUpdate) {
        this.onUpdate = onUpdate;
        this.program = [];
        this.loadLibrary();
    }
    
    updateContext() {
        this.onUpdate(this.program.join(''));
    }
    
    async loadLibrary() {
        try {
            const lib = await API.getLibrary();
            const container = document.getElementById('library-programs');
            if(!container || !lib) return;
            container.innerHTML = '';
            
            for(let [name, code] of Object.entries(lib)) {
                let btn = document.createElement('button');
                btn.className = 'full-width-btn';
                btn.textContent = name;
                btn.onclick = () => {
                    const input = document.getElementById('program-input');
                    if(input) input.value = code;
                    const drawer = document.getElementById('library-drawer');
                    if(drawer) drawer.classList.add('collapsed');
                };
                container.appendChild(btn);
            }
        } catch (e) {
            console.error("Library extraction failed:", e);
        }
    }
}
