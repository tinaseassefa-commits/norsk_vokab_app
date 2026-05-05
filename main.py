import json
import random
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# ---------- STATIC FILES ----------
@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/style.css")
async def serve_css():
    return FileResponse(BASE_DIR / "style.css")

@app.get("/script.js")
async def serve_js():
    return FileResponse(BASE_DIR / "script.js")


# ---------- HELPER ----------
def generate_audio_if_missing(text, path):
    if not path.exists():
        try:
            tts = gTTS(text=text, lang='no')
            tts.save(str(path))
        except Exception as e:
            print("TTS error:", e)


# ---------- API ----------
@app.get("/word-list")
async def get_word_list(request: Request):
    try:
        # Dynamically detect correct base URL (works everywhere)
        base_url = str(request.base_url).rstrip("/")

        with open(BASE_DIR / "vocabulary.json", "r", encoding="utf-8") as f:
            vocab_data = json.load(f)

        if not isinstance(vocab_data, dict):
            return JSONResponse(status_code=500, content={"error": "Invalid JSON format"})

        all_words = []

        for family, words in vocab_data.items():
            for w in words:
                new_word = w.copy()
                new_word["family"] = family
                all_words.append(new_word)

        if not all_words:
            return []

        selected = random.sample(all_words, min(len(all_words), 10))

        for item in selected:
            safe_name = item['word'].lower().replace(' ', '_')

            word_fn = f"word_{safe_name}.mp3"
            ex_fn = f"ex_{safe_name}.mp3"

            word_path = AUDIO_DIR / word_fn
            ex_path = AUDIO_DIR / ex_fn

            # Generate audio only if missing
            generate_audio_if_missing(item['word'], word_path)

            if item.get("example_norsk"):
                generate_audio_if_missing(item["example_norsk"], ex_path)

            # ✅ Correct absolute URLs
            item["audio_word"] = f"{base_url}/audio/{word_fn}"
            item["audio_example"] = (
                f"{base_url}/audio/{ex_fn}" if item.get("example_norsk") else None
            )

        return selected

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ---------- RUN ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))