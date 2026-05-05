const API_BASE = window.location.origin;

let currentWords = [];
let currentIndex = 0;

// SMART LOCK STATE
let mode = "explore"; // "explore" | "playall"
let isPlaying = false;
let isPaused = false;

window.onload = () => {
    fetchNewList();
    setupSwipe();
};

async function fetchNewList() {
    const status = document.getElementById("status");
    status.innerText = "Laster inn...";

    try {
        const res = await fetch(`${API_BASE}/word-list`);
        currentWords = await res.json();

        currentIndex = 0;
        mode = "explore";

        renderCurrentWord();
        status.innerText = "Klar!";
    } catch (err) {
        console.error(err);
        status.innerText = "Feil ved lasting.";
    }
}

function renderCurrentWord() {
    const container = document.getElementById("word-list-container");
    const item = currentWords[currentIndex];

    if (!item) return;

    container.innerHTML = `
        <div class="word-item">

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

            <div style="display:flex; gap:10px; margin-top:15px;">
                <button class="audio-btn" onclick="prevWord()">⬅ Prev</button>
                <button class="audio-btn" onclick="nextWord()">Next ➡</button>
            </div>

        </div>
    `;

    document.getElementById("status").innerText =
        `${currentIndex + 1} / ${currentWords.length}`;
}

/* ---------------- NAVIGATION (EXPLORE MODE ONLY) ---------------- */

function nextWord() {
    if (mode !== "explore") return;

    if (currentIndex < currentWords.length - 1) {
        currentIndex++;
        renderCurrentWord();
    }
}

function prevWord() {
    if (mode !== "explore") return;

    if (currentIndex > 0) {
        currentIndex--;
        renderCurrentWord();
    }
}

/* ---------------- AUDIO ---------------- */

function playAudio(url) {
    if (!url) return;

    const audio = new Audio(url);
    audio.play().catch(console.error);
}

/* ---------------- SPILL ALLE (SMART LOCK) ---------------- */

async function playAllSequentially() {
    if (isPlaying) return;

    mode = "playall";
    isPlaying = true;
    isPaused = false;

    const status = document.getElementById("status");

    for (currentIndex = 0; currentIndex < currentWords.length; currentIndex++) {

        renderCurrentWord();
        status.innerText = `Spiller: ${currentIndex + 1}/${currentWords.length}`;

        const item = currentWords[currentIndex];

        // WAIT if paused
        while (isPaused) {
            await sleep(300);
        }

        if (!isPlaying) break;

        if (item.audio_word) {
            await playAudioAsync(item.audio_word);
        }

        await sleep(500);

        if (item.audio_example) {
            await playAudioAsync(item.audio_example);
        }

        await sleep(900);
    }

    isPlaying = false;
    mode = "explore";
    status.innerText = "Ferdig!";
}

/* ---------------- PAUSE / RESUME / STOP ---------------- */

function pausePlayAll() {
    isPaused = true;
}

function resumePlayAll() {
    if (!isPlaying) return;
    isPaused = false;
}

function stopPlayAll() {
    isPlaying = false;
    isPaused = false;
    mode = "explore";
}

/* ---------------- AUDIO PROMISE ---------------- */

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

/* ---------------- SWIPE SUPPORT ---------------- */

function setupSwipe() {
    let startX = 0;

    document.addEventListener("touchstart", e => {
        startX = e.touches[0].clientX;
    });

    document.addEventListener("touchend", e => {
        const endX = e.changedTouches[0].clientX;

        if (mode !== "explore") return;

        if (startX - endX > 50) nextWord(); // swipe left
        if (endX - startX > 50) prevWord(); // swipe right
    });
}