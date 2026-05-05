const API_BASE = window.location.origin;

let currentWords = [];
let isPlaying = false;

window.onload = () => {
    fetchNewList();
};

async function fetchNewList() {
    const status = document.getElementById("status");
    status.innerText = "Laster inn...";

    try {
        const res = await fetch(`${API_BASE}/word-list`);
        if (!res.ok) throw new Error("API error");

        currentWords = await res.json();
        renderWords();

        status.innerText = "Oppdatert!";
    } catch (err) {
        console.error(err);
        status.innerText = "Kunne ikke laste ord.";
    }
}

function renderWords() {
    const container = document.getElementById("word-list-container");
    container.innerHTML = "";

    currentWords.forEach(item => {
        const div = document.createElement("div");
        div.className = "word-item";

        div.innerHTML = `
            <div class="word-header">
                <span class="norwegian-text">
                    ${item.word} ${item.kjønn ? `(${item.kjønn})` : ""}
                </span>
                <button class="audio-btn" onclick="playAudio('${item.audio_word}')">
                    🔊 Ord
                </button>
            </div>

            <p><em>${item.meaning || ""}</em></p>

            <div class="example-box">
                <p class="ex-norsk">${item.example_norsk || ""}</p>
                <p class="ex-eng">${item.example || ""}</p>

                ${item.audio_example ? `
                    <button class="audio-btn" onclick="playAudio('${item.audio_example}')">
                        🔊 Eksempel
                    </button>
                ` : ""}
            </div>
        `;

        container.appendChild(div);
    });
}

function playAudio(url) {
    if (!url) return;

    const audio = new Audio(url);
    audio.play().catch(err => console.error("Audio error:", err));
}

async function playAllSequentially() {
    if (isPlaying) return;
    isPlaying = true;

    const status = document.getElementById("status");
    status.innerText = "Spiller...";

    for (const item of currentWords) {
        if (item.audio_word) await playAudioAsync(item.audio_word);
        await sleep(500);

        if (item.audio_example) await playAudioAsync(item.audio_example);
        await sleep(900);
    }

    isPlaying = false;
    status.innerText = "Ferdig!";
}

function playAudioAsync(url) {
    return new Promise(resolve => {
        if (!url) return resolve();

        const audio = new Audio(url);
        audio.onended = resolve;
        audio.onerror = resolve;

        audio.play().catch(resolve);
    });
}

function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}