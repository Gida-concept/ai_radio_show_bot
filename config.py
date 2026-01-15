"""
config.py
Configuration for the 1-on-1 Interview Format.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# --- Environment Setup ---
load_dotenv()

# --- Project Structure ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Subdirectories
AUDIO_DIR = TEMP_DIR / "audio"
SUBTITLES_DIR = TEMP_DIR / "subtitles"
VIDEO_DIR = TEMP_DIR / "video"
PARTS_DIR = TEMP_DIR / "parts"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

# --- Scheduling ---
SHOW_INTERVAL_SECONDS = 11400 # 3h 10m
POSTING_INTERVAL_SECONDS = 600 # 10m

# --- Show Settings (1 vs 1) ---
NUM_HOSTS = 1
NUM_GUESTS = 1
CHARACTERS_JSON_PATH = DATA_DIR / "characters.json"

# --- Media Generation ---
# Target part length: 2.5 minutes
PART_DURATION_SECONDS = 150

# --- Groq Configuration ---
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3"

# --- Media Assets ---
BACKGROUND_VIDEO_URL = "res.cloudinary.com/dv0unfuhw/video/upload/v1767956311/dzvb8fvjditgqce3azbz.mp4"
BACKGROUND_MUSIC_URL = "https://res.cloudinary.com/dv0unfuhw/video/upload/v1767958481/sndhmaxhxvpz1veablza.mp3"

# --- Posting ---
POSTING_CAPTION_TEMPLATE = "💔 The Ex-Files: {host} sits down with {guest} to talk about heartbreak, betrayal, and moving on. #fyp #viralreels #reels #viral #Dating #Interview #RelationshipAdvice"

# --- Logging ---
LOG_FILE = LOGS_DIR / "ai_radio_bot.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

if not GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY is not set.")

