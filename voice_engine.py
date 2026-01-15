"""
voice_engine.py

Handles all text-to-speech (TTS) operations using Coqui TTS.
- ENFORCES 4 DISTINCT VOICES (2 MALE, 2 FEMALE).
- INCLUDES GENDER SAFETY FALLBACK.
- LOGS EVERY SPEAKER ASSIGNMENT VISIBLY.
"""

import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment

import config
from character_manager import CharacterManager

# --- VOICE MAPPING ---
# Maps abstract character voice keys to specific VCTK Speaker IDs.
# p226: Deep Male (Host Jack)
# p225: Clear Female (Host Olivia)
# p232: Distinct Male (Guest Ryan/Leo)
# p228: Distinct Female (Guest Mia/Chloe)
VOICE_MODEL_MAP = {
    # HOSTS
    "vits_male_01":   {"speaker": "p226"},
    "vits_female_01": {"speaker": "p225"},
    
    # GUESTS
    "vits_male_02":   {"speaker": "p232"},
    "vits_female_02": {"speaker": "p228"},
}

class VoiceEngine:
    """Manages TTS models and audio generation."""

    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        
        # Check for GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS will use device: {self.device.upper()}")
        
        # Load the VCTK VITS Model
        self.logger.info("Initializing Coqui TTS model (vctk/vits)...")
        try:
            self.tts = TTS("tts_models/en/vctk/vits").to(self.device)
            self.logger.info("Successfully loaded VCTK VITS model.")
        except Exception as e:
            self.logger.critical(f"CRITICAL: Failed to load TTS model. Error: {e}")
            raise RuntimeError("Could not load required TTS model.") from e

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Starting audio generation for {len(script)} script lines.")
        
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        line_audio_metadata = []
        combined_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            text = line["text"]
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                # 1. Look up the character
                character = self.character_manager.get_character_by_id(speaker_id)
                voice_key = character["voice"] # e.g., "vits_female_02"
                
                # 2. Determine Speaker ID
                if voice_key in VOICE_MODEL_MAP:
                    # Ideal case: We have a specific map for this key (e.g. Guest Female -> p228)
                    speaker = VOICE_MODEL_MAP[voice_key]["speaker"]
                else:
                    # Fallback Logic:
                    # If the key is missing (e.g. "vits_female_03"), we MUST check gender
                    # to prevent a female using a male voice.
                    if character['gender'] == 'male':
                        speaker = "p226" # Default to Host Male voice
                    else:
                        speaker = "p225" # Default to Host Female voice
                    self.logger.warning(f"Voice key '{voice_key}' not found. Fallback to {speaker} based on gender.")

                # --- VISIBLE LOGGING (INFO LEVEL) ---
                self.logger.info(f"Line {i+1}: {character['name']} ({character['gender']}) -> Speaker {speaker}")
                # ------------------------------------

                # 3. Generate audio
                self.tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=str(line_filename)
                )

                # 4. Add to master track
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
                continue
        
        # Export the final combined audio track
        master_audio_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_audio_path, format="wav")

        total_duration_s = len(combined_audio) / 1000
        self.logger.info(f"[{show_id}] Master audio track created at: {master_audio_path}")
        self.logger.info(f"[{show_id}] Total audio duration: {total_duration_s:.2f} seconds.")

        return str(master_audio_path), line_audio_metadata
