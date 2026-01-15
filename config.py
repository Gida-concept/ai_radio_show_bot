"""
config.py

Centralized configuration for the AI Radio Show Bot.
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
# 3 hours + 10 minutes = 11400 seconds
SHOW_INTERVAL_SECONDS = 11400

# Post every 10 minutes
POSTING_INTERVAL_SECONDS = 600

# --- Show Generation Settings ---
# STRICT LENGTH REQUIREMENTS
MIN_SHOW_DURATION_MINUTES = 8
MAX_SHOW_DURATION_MINUTES = 12

# Character setup
NUM_HOSTS = 2
NUM_GUESTS = 2
CHARACTERS_JSON_PATH = DATA_DIR / "characters.json"

# --- Media Generation ---
# Split video into 2.5 minute parts (150 seconds)
PART_DURATION_SECONDS = 150

# --- Groq Configuration ---
# USING THE LATEST MODEL
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"
GROQ_WHISPER_MODEL = "whisper-large-v3"

# --- Voice Engine ---
# These keys map to the strict gender enforcement in voice_engine.py
AVAILABLE_VOICES = [
    "vits_male_01",
    "vits_female_01",
    "vits_male_02",
    "vits_female_02",
]

# --- Video Engine ---
BACKGROUND_VIDEO_URL = "https://res.cloudinary.com/dv0unfuhw/video/upload/v1767956316/qg35pfueznxeene9xmhi.mp4"
BACKGROUND_MUSIC_URL = "https://res.cloudinary.com/dv0unfuhw/video/upload/v1767958481/sndhmaxhxvpz1veablza.mp3"

# --- Posting Engine ---
POSTING_CAPTION_TEMPLATE = "Date Update! 💘 Will {guest1} and {guest2} find love? Our hosts {host1} and {host2} get all the details. #AIRadio #DatingShow #AI"

# --- Logging ---
LOG_FILE = LOGS_DIR / "ai_radio_bot.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

if not GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY is not set.")
