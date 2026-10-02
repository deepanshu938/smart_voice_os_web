import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Base Paths
USER_HOME = Path.home()
DOWNLOADS_DIR = USER_HOME / "Downloads"
DESKTOP_DIR = USER_HOME / "Desktop"
DOCUMENTS_DIR = USER_HOME / "Documents"
PICTURES_DIR = USER_HOME / "Pictures"
VIDEOS_DIR = USER_HOME / "Videos"

# Primary Search Paths (Where 95%+ of user files reside)
CORE_SEARCH_DIRS = [
    DOWNLOADS_DIR,
    DESKTOP_DIR,
    DOCUMENTS_DIR,
    PICTURES_DIR,
    VIDEOS_DIR
]

# Blacklisted Folders (Never scan these to avoid freezing/infinite loops)
SYSTEM_BLACKLIST_DIRS = {
    "AppData", "node_modules", ".git", ".vscode", "Windows",
    "Program Files", "Program Files (x86)", "venv", ".venv",
    "__pycache__", "Local Settings", "Application Data", ".gemini"
}

# Supported Extensions for Inspection
EXT_MAP = {
    "document": {".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".xlsx", ".pptx"},
    "image": {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"},
    "archive": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".json", ".sql", ".sh"},
    "media": {".mp3", ".wav", ".mp4", ".mkv", ".mov"}
}

# API Credentials
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").strip().lower()

# Model Definitions (Verified working model on your Groq cluster)
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
GEMINI_MODEL = "gemini-2.5-flash"

# Voice Settings
VOICE_NAME = os.getenv("VOICE_NAME", "en-US-ChristopherNeural")
VOICE_RATE = os.getenv("VOICE_RATE", "+0%")

# Gmail Settings (App Password — see .env for setup instructions)
GMAIL_ADDRESS      = os.getenv("GMAIL_ADDRESS", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()

# Smart Home
KASA_DEVICE_IP = os.getenv("KASA_DEVICE_IP", "").strip()
HUE_BRIDGE_IP  = os.getenv("HUE_BRIDGE_IP", "").strip()
HUE_USERNAME   = os.getenv("HUE_USERNAME", "").strip()

