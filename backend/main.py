import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Ensure the project root (where `agent` lives) is on the path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.agent_controller import AgentController

app = FastAPI(title="AURA Smart Voice OS API")

# Initialise once – reuse the same controller for all requests
controller = AgentController()

class TextQuery(BaseModel):
    query: str

@app.post("/chat/text")
async def chat_text(payload: TextQuery):
    """Receive a text query and return the spoken answer as JSON."""
    try:
        # The controller returns a string answer (already TTS‑spoken on the server)
        answer = await controller.process_user_query(payload.query)
        return JSONResponse({"answer": answer})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/chat/audio")
async def chat_audio(file: UploadFile = File(...)):
    """Receive a recorded WAV/MP3, run STT, then forward to the controller.
    The result is streamed back as text (the LLM answer)."""
    if file.content_type not in ("audio/wav", "audio/mpeg", "audio/mp3"):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    audio_bytes = await file.read()
    # The `AgentController` already ships with its own STT/TTS pipeline.
    # For simplicity we use the same text‑query method – you can extend it.
    # Here we just return a placeholder response.
    return JSONResponse({"answer": "Audio processing not implemented yet – use /chat/text."})
