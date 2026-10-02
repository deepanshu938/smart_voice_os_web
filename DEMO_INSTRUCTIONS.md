# Demo & Resume Project Instructions

## Overview
This repository (**smart_voice_os_web**) contains a **full‑stack web version** of the **AURA Smart Voice OS** you built.  It showcases all the advanced features you added (email, calendar, file operations, smart‑home, news, weather, etc.) via a clean HTTP API and a tiny React UI.

## Project Structure (already created)
```
smart_voice_os_web/
├─ backend/                 # FastAPI server – entry point is `backend/main.py`
│   ├─ agent/               # Same code you already have (LLM client, controller, …)
│   ├─ core/                # System, OS & advanced tools
│   ├─ .env.example
│   ├─ requirements.txt
│   └─ main.py              # FastAPI routes (`/chat/text`, `/chat/audio`)
├─ frontend/                # React front‑end (create‑react‑app style)
│   ├─ public/index.html
│   └─ src/
│       ├─ App.js
│       ├─ index.js
│       └─ api.js
├─ .gitignore
├─ README.md                # High‑level repo description (you can keep it)
└─ README_WEB_PROJECT.md    # Detailed setup & demo guide (this file)
```

## 1️⃣ Set‑up locally (Windows PowerShell example)
```powershell
# ----- Clone the repo (replace <repo‑url> with your URL) -----
git clone <repo‑url>
cd smart_voice_os_web

# ----- Backend ------------------------------------------------
cd backend
python -m venv venv
venv\Scripts\activate   # activate virtual‑env
pip install -r requirements.txt
Copy-Item .env.example .env   # edit the .env with your keys (Groq, Gmail, etc.)
# Run the server (will listen on http://127.0.0.1:8000)
uvicorn main:app --reload

# ----- In a new terminal window, start the front‑end ---------
cd ..\frontend
npm install   # installs React + axios
npm start      # opens http://localhost:3000 in your browser
```
The UI lets you type a command **or** press **Start Voice** to record and send audio.  All AURA capabilities are now reachable via the web UI.

## 2️⃣ Packaging for your résumé
1. **Create a GitHub repo** and push the `smart_voice_os_web` folder.
2. Add a short description in the repo's **README.md** (the one already present).
3. In the **Projects** section of your résumé, list:
   - *"AURA Smart Voice OS – Full‑stack web demo (FastAPI + React). Integrated email, calendar, file ops, smart‑home, news, weather, voice I/O."
   - Include the repo URL.

## 3️⃣ Recording a demo video (≈ 1 min)
You can use **ffmpeg** (already bundled with most Windows builds) to capture the browser window while you interact with AURA.
```powershell
# Install ffmpeg if not present (skip if already installed)
# choco install ffmpeg   # or download from https://ffmpeg.org

# Record the screen region of the browser (adjust -video_size & -framerate)
ffmpeg -f gdigrab -framerate 30 -i title="AURA – Smart Voice OS" -video_size 1280x720 -t 60 demo.mp4
```
- Open `http://localhost:3000`.
- Type a few commands (e.g., *"weather Delhi"*, *"send email to alice@example.com"*, *"turn on the living‑room light"*).
- Stop recording – `demo.mp4` will be created in the current folder.
- Trim if needed:
```powershell
ffmpeg -i demo.mp4 -ss 00:00:05 -t 00:00:45 -c copy demo_trimmed.mp4
```
- Upload `demo_trimmed.mp4` to YouTube (unlisted) or directly attach it to your boss’s email.

## 4️⃣ Quick‑start script (run‑all‑in‑one)
Create a PowerShell script **run_demo.ps1** in the repo root:
```powershell
# run_demo.ps1 – one‑click launch for demo

# Start backend (in a new window)
Start-Process "powershell" -ArgumentList "-NoExit -Command `"cd $PWD\backend; .\venv\Scripts\activate; uvicorn main:app --reload`""

# Wait a few seconds for the server to be ready
Start-Sleep -Seconds 5

# Start front‑end (in another window)
Start-Process "powershell" -ArgumentList "-NoExit -Command `"cd $PWD\frontend; npm start`""

Write-Host "🚀 AURA demo is running – open http://localhost:3000 in your browser"
```
Running `.un_demo.ps1` will open two PowerShell windows, start the FastAPI server and the React UI, and print a friendly message.

## 5️⃣ What to showcase in the video
| Step | Command (type / speak) | Expected AURA action |
|------|-----------------------|----------------------|
| 1    | **weather Delhi**      | Reads weather and speaks it back |
| 2    | **send email to bob@example.com subject Test body Hello Bob!** | Sends a Gmail email (check Sent folder) |
| 3    | **create calendar event title Meeting date tomorrow time 14:00** | Opens a `.ics` file in Windows Calendar |
| 4    | **turn on the living‑room light** | Uses TP‑Link Kasa (if configured) |
| 5    | **open chrome and spotify** | Opens both apps together |
| 6    | **quick note note: Remember to review PR** | Saves a note file on Desktop and opens Notepad |

Each interaction appears as a short text bubble in the UI and is spoken aloud by the server (via the existing TTS engine).

---
### 🎬 Send to your boss
1. Record the demo (`demo_trimmed.mp4`).
2. Upload to YouTube **Unlisted** and copy the link.
3. Write a brief email:
```
Subject: AURA – AI‑Powered Voice OS Demo

Hi [Boss Name],

Please find the short demo video of the AURA Smart Voice OS (link below).  The project is fully functional, hosted on GitHub, and can be run locally with a single PowerShell script.

Demo: <YouTube‑link>
Repo: <GitHub‑repo‑url>

Best,
[Your Name]
```
That’s it – you now have a polished project you can proudly add to your résumé and showcase to your boss! 🚀
