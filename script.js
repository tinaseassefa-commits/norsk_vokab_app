const API_BASE = "https://norsk-vokab-app-1.onrender.com";
let currentWords = [];
let isPlaying = false;

window.onload = () => {
    const saved = localStorage.getItem('norskSavedWords');
    if (saved) {
        try {
            currentWords = JSON.parse(saved);
            renderWords();
        } catch (e) {
            fetchNewList();
        }
    } else {
        fetchNewList();
    }
};

async function fetchNewList() {
    const status = document.getElementById('status');
    if (status) status.innerText = "Laster inn...";
    
    try {
        const response = await fetch(`${API_BASE}/word-list`);
        if (!response.ok) throw new Error('Nettverksfeil');
        
        currentWords = await response.json();
        localStorage.setItem('norskSavedWords', JSON.stringify(currentWords));
        renderWords();
        
        if (status) status.innerText = "Oppdatert!";
    } catch (error) {
        console.error("Fetch error:", error);
        if (status) status.innerText = "Serverfeil. Prøv igjen senere.";
    }
}

function renderWords() {
    const container = document.getElementById('word-list-container');
    if (!container) return;
    
    container.innerHTML = '';
    currentWords.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'word-item';
        
        // Note: We use item.audio_word directly because it already contains "/audio/..."
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center">
                <span class="norwegian-text">${item.word} (${item.kjønn || ''})</span>
                <button class="audio-btn" onclick="playAudio('${item.audio_word}')">🔊 Ord</button>
            </div>
            <p><em>${item.meaning}</em></p>
            <p><strong>${item.example_norsk || ''}</strong></p>
            ${item.audio_example ? 
                `<button class="audio-btn" onclick="playAudio('${item.audio_example}')">🔊 Eksempel</button>` : 
                ''}
        `;
        container.appendChild(div);
    });
}

// Simple play function for buttons
function playAudio(url) {
    if (!url || url === "null") return;
    // The browser will automatically combine your domain with this /audio/ path
    const audio = new Audio(url); 
    audio.play().catch(err => console.error("Error:", err));
}
// Sequential play logic
async function playAllSequentially() {
    if (isPlaying) return;
    isPlaying = true;
    
    const status = document.getElementById('status');
    if (status) status.innerText = "Spiller av alle...";

    for (const item of currentWords) {
        if (item.audio_word) {
            await playAudioAsync(item.audio_word);
        }
        await new Promise(r => setTimeout(r, 600));
        
        if (item.audio_example) {
            await playAudioAsync(item.audio_example);
        }
        await new Promise(r => setTimeout(r, 1200));
    }
    
    isPlaying = false;
    if (status) status.innerText = "Ferdig!";
}

// Helper to wait for audio to finish before next one starts
function playAudioAsync(url) {
    return new Promise((resolve) => {
        if (!url || url === "null") {
            resolve();
            return;
        }
        const audio = new Audio(url);
        audio.onended = resolve;
        audio.onerror = (e) => {
            console.error("Audio error:", e);
            resolve();
        };
        audio.play().catch(err => {
            console.error("Play error:", err);
            resolve();
        });
    });
}