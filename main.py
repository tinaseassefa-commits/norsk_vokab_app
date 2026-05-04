import json
import random
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Identify where the files are
BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 1. Mount the audio folder to /audio
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# 2. EXPLICIT FILE ROUTES
@app.get("/")
async def serve_index():
    return FileResponse(str(BASE_DIR / "index.html"))

@app.get("/style.css")
async def serve_css():
    return FileResponse(str(BASE_DIR / "style.css"), media_type="text/css")

@app.get("/script.js")
async def serve_js():
    return FileResponse(str(BASE_DIR / "script.js"), media_type="application/javascript")

# 3. WORD LIST LOGIC
@app.get("/word-list")
async def get_word_list():
    try:
        with open(BASE_DIR / "vocabulary.json", "r", encoding="utf-8") as f:
            vocab_data = json.load(f)
        
        all_words = []
        for family, words in vocab_data.items():
            for w in words:
                w['family'] = family
                all_words.append(w)
        
        selected = random.sample(all_words, min(len(all_words), 10))
        
        for item in selected:
            safe_name = item['word'].lower().replace(' ', '_')
            word_fn, ex_fn = f"word_{safe_name}.mp3", f"ex_{safe_name}.mp3"
            
            # Physical save
            word_path = AUDIO_DIR / word_fn
            ex_path = AUDIO_DIR / ex_fn

            if not word_path.exists():
                gTTS(text=item['word'], lang='no').save(str(word_path))
            
            if item.get('example_norsk') and not ex_path.exists():
                gTTS(text=item['example_norsk'], lang='no').save(str(ex_path))

            # Virtual URLs for the frontend
            item['audio_word'] = f"/audio/{word_fn}"
            item['audio_example'] = f"/audio/{ex_fn}" if item.get('example_norsk') else None

        return selected
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))