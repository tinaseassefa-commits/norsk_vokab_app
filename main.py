import json
import random
import os
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

# 2. SETUP DIRECTORIES
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. LOAD DATA (Do this before any routes!)
# This ensures vocab_data is defined as soon as the app starts
try:
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        vocab_data = json.load(f)
    print("Successfully loaded vocabulary.json")
except Exception as e:
    print(f"Error loading JSON: {e}")
    # Fallback so the app doesn't crash if the file is missing
    vocab_data = {"Error": [{"word": "Error", "meaning": "Check JSON file", "example": "", "fun_fact": "", "image_keyword": "error"}]}

# 4. THE HOME PAGE (Fixes "Not Found")
@app.get("/")
async def serve_index():
    return FileResponse('index.html')

# 5. THE API ENGINE
@app.get("/word-of-the-day")
async def get_word():
    # This now safely uses the vocab_data defined above
    family_name = random.choice(list(vocab_data.keys()))
    word_item = random.choice(vocab_data[family_name])
    word_text = word_item['word']
    
    filename = f"{word_text.lower()}.mp3"
    filepath = os.path.join("static/audio", filename)
    
    if not os.path.exists(filepath):
        tts = gTTS(text=word_text, lang='no')
        tts.save(filepath)
    
    return {
        "family": family_name,
        "word": word_text,
        "meaning": word_item['meaning'],
        "example_norsk": word_item.get('example_norsk', 'Ingen eksempel tilgjengelig'),
        "example": word_item['example'],
        "fun_fact": word_item['fun_fact'],
        "image": f"https://loremflickr.com/400/300/{word_item['image_keyword']}",
        "audio": f"/static/audio/{filename}"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)