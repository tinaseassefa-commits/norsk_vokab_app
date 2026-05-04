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

# 1. CORS SETTINGS (Allows your frontend to talk to your backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. PATH & DIRECTORY SETUP
# Get the absolute path of the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the physical audio folder inside the project
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Mount the audio folder so files are accessible at /audio/filename.mp3
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# 3. DIRECT FILE ROUTES (Bypasses "Static" folder issues)
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, 'index.html'))

@app.get("/style.css")
async def serve_css():
    return FileResponse(os.path.join(BASE_DIR, 'style.css'))

@app.get("/script.js")
async def serve_js():
    return FileResponse(os.path.join(BASE_DIR, 'script.js'))

# 4. DATA LOADING
try:
    with open(os.path.join(BASE_DIR, "vocabulary.json"), "r", encoding="utf-8") as f:
        vocab_data = json.load(f)
    print("Vocabulary loaded successfully.")
except Exception as e:
    print(f"Error loading JSON: {e}")
    vocab_data = {}

# 5. WORD LIST LOGIC
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

        # Generate unique filenames
        safe_name = word_text.lower().replace(' ', '_')
        word_filename = f"word_{safe_name}.mp3"
        ex_filename = f"ex_{safe_name}.mp3"

        # Physical paths to save files
        word_path = os.path.join(AUDIO_DIR, word_filename)
        ex_path = os.path.join(AUDIO_DIR, ex_filename)

        # Generate Audio if it doesn't exist
        if not os.path.exists(word_path):
            gTTS(text=word_text, lang='no').save(word_path)
        
        if example_text and not os.path.exists(ex_path):
            gTTS(text=example_text, lang='no').save(ex_path)

        # Set the URLs the browser will use to play the sound
        item['audio_word'] = f"/audio/{word_filename}"
        item['audio_example'] = f"/audio/{ex_filename}" if example_text else None

    return selected_words

if __name__ == "__main__":
    # Get port from environment (for Render) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)