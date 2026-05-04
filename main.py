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
# Create the folders if they don't exist
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return FileResponse('index.html')

# 5. THE NEW LIST GENERATOR (10 Words)
@app.get("/word-list")
async def get_word_list():
    # Flatten all categories into a single list
    all_words = []
    for family, words in vocab_data.items():
        for w in words:
            w['family'] = family
            all_words.append(w)
    
    # Pick 10 random words (or fewer if the list is small)
    sample_size = min(len(all_words), 10)
    selected_words = random.sample(all_words, sample_size)
    
    for item in selected_words:
        word_text = item['word']
        example_text = item.get('example_norsk', '')

        # Generate Audio for the WORD
        word_filename = f"word_{word_text.lower().replace(' ', '_')}.mp3"
        word_path = os.path.join("static/audio", word_filename)
        if not os.path.exists(word_path):
            gTTS(text=word_text, lang='no').save(word_path)
        item['audio_word'] = f"/static/audio/{word_filename}"

        # Generate Audio for the EXAMPLE
        if example_text:
            ex_filename = f"ex_{word_text.lower().replace(' ', '_')}.mp3"
            ex_path = os.path.join("static/audio", ex_filename)
            if not os.path.exists(ex_path):
                gTTS(text=example_text, lang='no').save(ex_path)
            item['audio_example'] = f"/static/audio/{ex_filename}"
        else:
            item['audio_example'] = None

    return selected_words

if __name__ == "__main__":
    import uvicorn
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)