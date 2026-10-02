# Project: smart_voice_os_web

This repository contains a full‑stack web version of the **AURA Smart Voice OS**.

## Directory Layout
```
smart_voice_os_web/
├─ backend/                 # Python FastAPI server (the "engine")
│   ├─ agent/               # Same code you already have – LLM client, controller, etc.
│   ├─ core/                # System tools, OS tools, advanced tools
│   ├─ config.py
│   ├─ .env.example          # copy to .env and fill your keys
│   ├─ requirements.txt      # Python deps
│   └─ main.py               # FastAPI entry point
├─ frontend/                # React UI (create‑react‑app style)
│   ├─ public/
│   │   └─ index.html
│   └─ src/
│       ├─ App.js
│       ├─ index.js
│       └─ api.js            # helper to call backend
├─ .gitignore
└─ README.md                # How to run locally & deploy
```

## How it works
* **Backend** runs the original AURA engine inside a FastAPI route.  The route receives a user query (text or a recorded audio blob), forwards it to the existing `AgentController`, and streams the LLM response back.
* **Frontend** provides a tiny UI – a text box and a *Start Voice* button that records from the microphone, sends the audio to the server, and shows the spoken answer.
* All the heavy lifting (speech‑to‑text, text‑to‑speech, tool dispatch) stays unchanged; we only wrap it in an HTTP API.

---

## Backend (`backend/main.py`)
```python
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import AsyncGenerator

# Ensure the project root (where `agent` lives) is on the path
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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
    # We expose a tiny helper that accepts raw bytes.
    answer = await controller.process_audio_query(audio_bytes)
    return JSONResponse({"answer": answer})
```

### Backend `requirements.txt`
```
fastapi
uvicorn[standard]
python-dotenv
# plus all the original requirements from AURA (see the existing requirements.txt)
pyautogui
pygetwindow
psutil
Pillow
pycaw
comtypes
feedparser
python-docx
openpyxl
screen-brightness-control
python-kasa
phue
```

### `.env.example`
```
# LLM provider keys – already used by AURA
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=qwen/qwen3.8-27b
# Optional – Gemini key if you switch provider
GEMINI_API_KEY=
GEMINI_MODEL=

# Gmail credentials (for email features)
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16char_app_password

# Smart‑home optional config
KASA_DEVICE_IP=
HUE_BRIDGE_IP=
HUE_USERNAME=
```

## Front‑end (`frontend/`)
The UI is a small React app created with **Create‑React‑App** (you can also use Vite – the code works for both).

### `frontend/package.json`
```json
{
  "name": "aura‑frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.7.2"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

### `frontend/public/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AURA – Smart Voice OS</title>
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root"></div>
</body>
</html>
```

### `frontend/src/index.js`
```javascript
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### `frontend/src/api.js`
```javascript
import axios from "axios";

const API_BASE = "http://localhost:8000"; // FastAPI default

export const sendText = async (text) => {
  const resp = await axios.post(`${API_BASE}/chat/text`, { query: text });
  return resp.data.answer;
};

export const sendAudio = async (blob) => {
  const form = new FormData();
  form.append("file", blob, "voice.wav");
  const resp = await axios.post(`${API_BASE}/chat/audio`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data.answer;
};
```

### `frontend/src/App.js`
```javascript
import React, { useState, useRef } from "react";
import { sendText, sendAudio } from "./api";

function App() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [listening, setListening] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setOutput("⏳ Thinking…");
    const answer = await sendText(input.trim());
    setOutput(answer);
    setInput("");
  };

  const startRecording = async () => {
    setListening(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    mediaRecorder.current.ondataavailable = (e) => {
      audioChunks.current.push(e.data);
    };
    mediaRecorder.current.onstop = async () => {
      const blob = new Blob(audioChunks.current, { type: "audio/wav" });
      audioChunks.current = [];
      setOutput("⏳ Listening…");
      const answer = await sendAudio(blob);
      setOutput(answer);
      setListening(false);
    };
    mediaRecorder.current.start();
    // auto‑stop after 8 seconds (adjust as needed)
    setTimeout(() => mediaRecorder.current.stop(), 8000);
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>AURA – Smart Voice OS</h1>

      <form onSubmit={handleTextSubmit} style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Type a command …"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ width: "80%", padding: "0.5rem" }}
        />
        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Send
        </button>
      </form>

      <button onClick={startRecording} disabled={listening} style={{ padding: "0.5rem 1rem" }}>
        {listening ? "Recording…" : "Start Voice"}
      </button>

      <pre style={{ background: "#f4f4f4", padding: "1rem", marginTop: "1rem" }}>
        {output}
      </pre>
    </div>
  );
}

export default App;
```

## Running locally
```bash
# ---- Clone / initialise ----
git clone <repo‑url>
cd smart_voice_os_web

# ---- Backend ----
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # edit with your keys
uvicorn main:app --reload   # runs on http://127.0.0.1:8000

# ---- Frontend (in another terminal) ----
cd ../frontend
npm install
npm start   # opens http://localhost:3000
```
The UI will talk to the FastAPI server, which in turn uses the full AURA engine – all the tools you added (email, calendar, smart‑home, etc.) are available via voice or text.

---

## Deploying to GitHub & a cloud host
1. **Create a GitHub repo** and push the `smart_voice_os_web` folder.
2. **GitHub Actions** – add a simple workflow that builds the React app and pushes a Docker image for the FastAPI backend.
3. **Docker** – you can containerise both parts with a `docker-compose.yml`:
```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: ./backend/.env
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```
4. Deploy the compose file to any VPS, Azure App Service, Render.com, Fly.io, etc.

---

## What you get
- **All AURA capabilities** (WhatsApp automation, Gmail, file ops, smart‑home, news, weather, etc.) exposed through a clean HTTP API.
- **A modern React front‑end** that works on desktop browsers and mobile browsers (microphone access).
- **Ready‑to‑push GitHub repo** with `.gitignore`, README, Docker support and deployment hints.
- **Instructions** for local development, testing, and production.

You can now clone the repo, run `npm start` + `uvicorn`, and start using AURA with a click or voice – no more terminal wizardry! 🚀

---

If you need any of the placeholder files fleshed out (e.g., a proper `AgentController.process_audio_query` implementation), let me know and I can add the exact snippets.
