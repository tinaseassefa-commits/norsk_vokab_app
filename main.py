import json
import random
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gtts import gTTS

app = FastAPI()

# 1. ALLOW ACCESS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. SETUP DIRECTORIES & MOUNTING
os.makedirs("audio", exist_ok=True)

# Get the absolute path to this project folder
base_path = os.path.dirname(os.path.abspath(__file__))

# Map the URL prefix "/static" to project folder
app.mount("/static", StaticFiles(directory=base_path), name="static")

# 3. LOAD DATA
try:
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        vocab_data = json.load(f)
    print("Vocabulary loaded successfully.")
except Exception as e:
    print(f"Error loading JSON: {e}")
    vocab_data = {}

# 4. SERVE THE FRONTEND
@app.get("/")
async def serve_index():
    # index.html is in the root folder
    return FileResponse('index.html')

# 5. THE WORD LIST GENERATOR
@app.get("/word-list")
async def get_word_list():
    all_words = []
    for family, words in vocab_data.items():
        for w in words:
            w['family'] = family
            all_words.append(w)
    
    sample_size = min(len(all_words), 10)
    selected_words = random.sample(all_words, sample_size)
    
    for item in selected_words:
        word_text = item['word']
        example_text = item.get('example_norsk', '')

        # Filenames
        word_filename = f"word_{word_text.lower().replace(' ', '_')}.mp3"
        ex_filename = f"ex_{word_text.lower().replace(' ', '_')}.mp3"

        # Physical Paths for Python (saving to the "audio" folder)
        word_path = os.path.join("audio", word_filename)
        ex_path = os.path.join("audio", ex_filename)

        # Generate files if missing
        if not os.path.exists(word_path):
            gTTS(text=word_text, lang='no').save(word_path)
        
        if example_text and not os.path.exists(ex_path):
            gTTS(text=example_text, lang='no').save(ex_path)

        # Virtual URLs for the Browser
        item['audio_word'] = f"/static/audio/{word_filename}"
        item['audio_example'] = f"/static/audio/{ex_filename}" if example_text else None

    return selected_words

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)