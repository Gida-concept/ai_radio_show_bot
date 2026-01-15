"""
voice_engine.py

Handles all text-to-speech (TTS) operations using Coqui TTS.
- Loads specified TTS models into memory.
- Generates speech for each line of the script with the correct character voice.
- Measures the duration of each generated audio clip.
- Concatenates individual audio clips into a single master audio track for the show.
"""

import os
import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment

import config
from character_manager import CharacterManager

# --- Coqui TTS Model & Speaker Mapping ---
# This dictionary maps the abstract voice names from characters.json to actual
# Coqui TTS models and specific speakers within those models.
#
# YOU MUST DOWNLOAD/PROVIDE THESE MODELS FOR TTS TO WORK.
# Example using VCTK model (multi-speaker):
#   - Model: "tts_models/en/vctk/vits"
#   - Speakers: "p225" (male), "p226" (female), "p227" (male), etc.
#
# Update this map based on the models you have installed.
VOICE_MODEL_MAP = {
    "vits_male_01": {"model_name": "tts_models/en/vctk/vits", "speaker": "p228"},
    "vits_female_01": {"model_name": "tts_models/en/vctk/vits", "speaker": "p232"},
    "vits_male_02": {"model_name": "tts_models/en/vctk/vits", "speaker": "p231"},
    "vits_female_02": {"model_name": "tts_models/en/vctk/vits", "speaker": "p230"},
}


class VoiceEngine:
    """Manages TTS models and audio generation."""

    def __init__(self, character_manager: CharacterManager):
        """
        Initializes the VoiceEngine.

        Args:
            character_manager: An instance of CharacterManager to resolve character details.
        """
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS will use device: {self.device.upper()}")
        self.tts_models = self._initialize_tts_models()

    def _initialize_tts_models(self) -> Dict[str, TTS]:
        """
        Loads all unique TTS models specified in VOICE_MODEL_MAP into memory.

        Returns:
            A dictionary mapping model names to loaded TTS objects.
        """
        loaded_models = {}
        unique_model_names = set(v['model_name'] for v in VOICE_MODEL_MAP.values())

        self.logger.info("Initializing Coqui TTS models...")
        for model_name in unique_model_names:
            try:
                self.logger.info(f"Loading TTS model: {model_name}")
                # Note: `progress_bar=False` is good for non-interactive server logs
                loaded_models[model_name] = TTS(model_name).to(self.device)
                self.logger.info(f"Successfully loaded {model_name}")
            except Exception as e:
                self.logger.critical(f"CRITICAL: Failed to load TTS model '{model_name}'. Error: {e}")
                # This is a fatal error, so we raise it to stop the application.
                raise RuntimeError(f"Could not load required TTS model: {model_name}") from e

        self.logger.info("All TTS models initialized successfully.")
        return loaded_models

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generates audio for an entire script and concatenates it into a single file.

        Args:
            script: A list of script lines (dictionaries with 'speaker_id', 'text').
            show_id: A unique identifier for the show run (e.g., timestamp).

        Returns:
            A tuple containing:
            - The file path to the final concatenated master audio file.
            - A list of dictionaries with metadata for each line (path, duration_ms, speaker_id).
        """
        self.logger.info(f"[{show_id}] Starting audio generation for {len(script)} script lines.")

        # Create a dedicated directory for this show's audio parts
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)

        line_audio_metadata = []
        combined_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            text = line["text"]
            line_filename = show_audio_dir / f"line_{i:03d}_speaker_{speaker_id}.wav"

            try:
                character = self.character_manager.get_character_by_id(speaker_id)
                voice_key = character["voice"]

                if voice_key not in VOICE_MODEL_MAP:
                    raise ValueError(
                        f"Voice '{voice_key}' for character '{character['name']}' not found in VOICE_MODEL_MAP.")

                model_info = VOICE_MODEL_MAP[voice_key]
                model_name = model_info["model_name"]
                speaker = model_info.get("speaker")  # Use .get() for flexibility

                tts_instance = self.tts_models[model_name]

                self.logger.debug(
                    f"Generating line {i + 1}/{len(script)} for speaker {speaker_id} ('{character['name']}').")

                # Generate audio file for the line
                tts_instance.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=str(line_filename)
                )

                # Measure duration and add to the combined track
                line_audio = AudioSegment.from_wav(line_filename)
                duration_ms = len(line_audio)
                combined_audio += line_audio

                line_audio_metadata.append({
                    "path": str(line_filename),
                    "duration_ms": duration_ms,
                    "speaker_id": speaker_id,
                    "text": text,
                })

            except Exception as e:
                self.logger.error(f"Failed to generate audio for line {i}: '{text}'. Error: {e}")
                # We'll continue, but this might result in a gap in the audio.
                # A more robust system might halt or retry.
                continue

        # Export the final combined audio track
        master_audio_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_audio_path, format="wav")

        total_duration_s = len(combined_audio) / 1000
        self.logger.info(f"[{show_id}] Master audio track created at: {master_audio_path}")
        self.logger.info(f"[{show_id}] Total audio duration: {total_duration_s:.2f} seconds.")

        return str(master_audio_path), line_audio_metadata