export const API = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (e) {
            console.error(`API Error at ${url}:`, e);
            return null;
        }
    },
    loadProgram: (text) => API.request('/api/load', { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({text}) 
    }),
    play: () => API.request('/api/play', { method: 'POST' }),
    pause: () => fetch('/api/pause', { method: 'POST' })
};
