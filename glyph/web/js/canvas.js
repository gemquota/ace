export class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.nodePositions = {};
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        const parent = this.canvas.parentElement;
        if(parent) {
            this.canvas.width = parent.clientWidth;
            this.canvas.height = parent.clientHeight;
        }
    }
    
    updatePhysics(stateData) {
        if(!stateData || !stateData.graph) return;
        const nodes = stateData.graph.nodes;
        const cw = this.canvas.width;
        const ch = this.canvas.height;
        
        nodes.forEach(n => {
            if(!this.nodePositions[n.id]) {
                this.nodePositions[n.id] = { x: cw/2 + (Math.random()-0.5)*50, y: ch/2 + (Math.random()-0.5)*50, vx: 0, vy: 0 };
            }
        });
        
        const repel = 500;
        for(let i=0; i<nodes.length; i++) {
            for(let j=i+1; j<nodes.length; j++) {
                let p1 = this.nodePositions[nodes[i].id];
                let p2 = this.nodePositions[nodes[j].id];
                let dx = p1.x - p2.x;
                let dy = p1.y - p2.y;
                let dist = Math.sqrt(dx*dx + dy*dy) || 1;
                if(dist < 100) {
                    let f = repel / (dist * dist);
                    p1.vx += (dx/dist)*f; p1.vy += (dy/dist)*f;
                    p2.vx -= (dx/dist)*f; p2.vy -= (dy/dist)*f;
                }
            }
        }

        nodes.forEach(n => {
            let p1 = this.nodePositions[n.id];
            (n.links || []).forEach(targetId => {
                let p2 = this.nodePositions[targetId];
                if(p2) {
                    let dx = p2.x - p1.x;
                    let dy = p2.y - p1.y;
                    let dist = Math.sqrt(dx*dx + dy*dy) || 1;
                    let f = (dist - 80) * 0.05;
                    p1.vx += (dx/dist)*f; p1.vy += (dy/dist)*f;
                    p2.vx -= (dx/dist)*f; p2.vy -= (dy/dist)*f;
                }
            });
            p1.vx += (cw/2 - p1.x) * 0.005;
            p1.vy += (ch/2 - p1.y) * 0.005;
            p1.vx *= 0.85; p1.vy *= 0.85;
            p1.x += p1.vx; p1.y += p1.vy;
        });
    }
    
    draw(stateData) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        if(!stateData || !stateData.graph) return;
        const nodes = stateData.graph.nodes;
        const activeNodes = stateData.active_nodes || [];
        const activeEdges = stateData.active_edges || [];
        
        this.ctx.lineWidth = 2;
        nodes.forEach(n => {
            let p1 = this.nodePositions[n.id];
            if(!p1) return;
            (n.links || []).forEach(targetId => {
                let p2 = this.nodePositions[targetId];
                if(p2) {
                    // Highlight active traversal edges in #ff0055
                    let isActiveEdge = activeEdges.some(e => e[0] === n.id && e[1] === targetId);
                    this.ctx.strokeStyle = isActiveEdge ? '#ff0055' : '#445566';
                    
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            });
        });

        nodes.forEach(n => {
            let p = this.nodePositions[n.id];
            if(!p) return;
            this.ctx.fillStyle = activeNodes.includes(n.id) ? '#ff0055' : '#112233';
            this.ctx.strokeStyle = '#00ffcc';
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, 15, 0, Math.PI*2);
            this.ctx.fill();
            this.ctx.stroke();
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = '14px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(n.glyph, p.x, p.y);
        });
    }
}
