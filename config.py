"""
config.py

Centralized configuration for the AI Radio Show Bot.
Reads sensitive data from a .env file and sets up constants for the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# --- Environment Setup ---
# Load environment variables from a .env file in the project root
# The .env file should contain your secret keys (GROQ_API_KEY, FACEBOOK_ACCESS_TOKEN, etc.)
# Create this file if it doesn't exist.
load_dotenv()

# --- Project Structure ---
# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Data directory for persistent data like character profiles
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Temporary file storage for generated media
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# Subdirectories for temporary files
AUDIO_DIR = TEMP_DIR / "audio"
SUBTITLES_DIR = TEMP_DIR / "subtitles"
VIDEO_DIR = TEMP_DIR / "video"
PARTS_DIR = TEMP_DIR / "parts" # For split video parts

# Logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# --- API Keys & Credentials ---
# IMPORTANT: Store these in your .env file, NOT here.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

# --- Scheduling ---
# Interval for starting a new show generation cycle.
# 3 hours and 10 minutes = (3 * 3600) + (10 * 60) = 11400 seconds.
SHOW_INTERVAL_SECONDS = 11400

# Interval for posting each split video part to social media.
# 10 minutes = 10 * 60 = 600 seconds.
POSTING_INTERVAL_SECONDS = 600

# --- Show Generation ---
# Duration range for the entire show in minutes.
MIN_SHOW_DURATION_MINUTES = 5
MAX_SHOW_DURATION_MINUTES = 10

# Character setup for the show
NUM_HOSTS = 2
NUM_GUESTS = 2
CHARACTERS_JSON_PATH = DATA_DIR / "characters.json"

# --- Media Generation ---
# The target duration for each split video part.
# 2.5 minutes = 2.5 * 60 = 150 seconds.
PART_DURATION_SECONDS = 150

# --- Groq Configuration ---
# Model for text generation. Llama3 70b is great for creative, conversational content.
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"

# Model for speech-to-text (subtitles). Whisper Large v3 is the most accurate.
GROQ_WHISPER_MODEL = "whisper-large-v3"

# --- Voice Engine (Coqui TTS) ---
# List of available VITS voices to validate against characters.json
# These should match the model names you have available in your TTS installation.
# Example: "tts_models/en/vctk/vits" and then specify speaker e.g., "p225"
# For this project, we assume simplified names that map to specific models.
# The voice_engine will handle the mapping from 'vits_male_01' to a real model path.
AVAILABLE_VOICES = [
    "vits_male_01",
    "vits_female_01",
    "vits_male_02",
    "vits_female_02",
]

# --- Video Engine (FFmpeg) ---
# Provide URLs to long-running background video and music.
# Using creative commons / royalty-free sources is recommended.
# Example: A long, looping animation or a static image with subtle movement.
BACKGROUND_VIDEO_URL = "https://res.cloudinary.com/dv0unfuhw/video/upload/v1767956316/qg35pfueznxeene9xmhi.mp4" # Looping abstract background

# Example: A long, royalty-free lo-fi or ambient music track.
BACKGROUND_MUSIC_URL = "https://res.cloudinary.com/dv0unfuhw/video/upload/v1767958481/sndhmaxhxvpz1veablza.mp3" # Ambient lofi track

# --- Posting Engine ---
# Template for the social media post caption.
# {hosts} and {guests} will be replaced with character names.
POSTING_CAPTION_TEMPLATE = "Date Update! 💘 Will {guest1} and {guest2} find love? Our hosts {host1} and {host2} get all the details. #AIRadio #DatingShow #AI"

# --- Logging ---
LOG_FILE = LOGS_DIR / "ai_radio_bot.log"
LOG_LEVEL = "INFO" # "DEBUG" for more verbose output
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

# --- Validation ---
# Basic checks to ensure critical configurations are set.
if not GROQ_API_KEY:
    raise ValueError("CRITICAL: GROQ_API_KEY is not set in the environment or .env file.")


print("Configuration loaded successfully.")

