# 📦 Import necessary tools
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel
from openai import OpenAI
from gtts import gTTS
from uuid import uuid4
import os
from dotenv import load_dotenv

# 🔐 Load your OpenAI key from .env file
# Load API Key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class TextRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat_endpoint(payload: dict):
    user_input = payload.get("user_input", "")

    if not user_input:
        return {"response": "No input provided."}

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    return {"response": completion.choices[0].message.content}

@app.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        temp_filename = "temp_audio.wav"
        with open(temp_filename, "wb") as f:
            f.write(await file.read())

        with open(temp_filename, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

        return {"text": transcript.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text-to-speech")
def text_to_speech(request: TextRequest):
    try:
        filename = f"{uuid4().hex}.mp3"
        tts = gTTS(request.text)
        tts.save(filename)
        return FileResponse(filename, media_type="audio/mpeg", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app18:app", host="0.0.0.0", port=8000)
