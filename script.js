const API_BASE = "https://norsk-vokab-app-1.onrender.com";
let currentWords = [];
let isPlaying = false;

window.onload = () => {
    const saved = localStorage.getItem('norskSavedWords');
    if (saved) {
        currentWords = JSON.parse(saved);
        renderWords();
    } else {
        fetchNewList();
    }
};

async function fetchNewList() {
    const status = document.getElementById('status');
    status.innerText = "Laster inn...";
    try {
        const response = await fetch(`${API_BASE}/word-list`);
        currentWords = await response.json();
        localStorage.setItem('norskSavedWords', JSON.stringify(currentWords));
        renderWords();
        status.innerText = "Oppdatert!";
    } catch (error) {
        status.innerText = "Serverfeil.";
    }
}

function renderWords() {
    const container = document.getElementById('word-list-container');
    container.innerHTML = '';
    currentWords.forEach((item) => {
        const div = document.createElement('div');
        div.className = 'word-item';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between">
                <span class="norwegian-text">${item.word} (${item.kjønn})</span>
                <button class="audio-btn" onclick="playAudio('${API_BASE}${item.audio_word}')">🔊 Ord</button>
            </div>
            <p>${item.meaning}</p>
            <p><strong>${item.example_norsk}</strong></p>
            <button class="audio-btn" onclick="playAudio('${API_BASE}${item.audio_example}')">🔊 Eksempel</button>
        `;
        container.appendChild(div);
    });
}

function playAudio(url) { new Audio(url).play(); }

async function playAllSequentially() {
    if (isPlaying) return;
    isPlaying = true;
    for (const item of currentWords) {
        await playAudioAsync(`${API_BASE}${item.audio_word}`);
        await new Promise(r => setTimeout(r, 500));
        await playAudioAsync(`${API_BASE}${item.audio_example}`);
        await new Promise(r => setTimeout(r, 1000));
    }
    isPlaying = false;
}

function playAudioAsync(url) {
    return new Promise((resolve) => {
        const audio = new Audio(url);
        audio.onended = resolve;
        audio.onerror = resolve;
        audio.play();
    });
}