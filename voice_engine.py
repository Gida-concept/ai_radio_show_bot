"""
voice_engine.py
- RESTORED TO STABLE GENERATIVE VERSION.
- 4 DISTINCT VOICES (VCTK Model).
- LOGS VISIBLE.
"""

import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment

import config
from character_manager import CharacterManager

# --- VOICE MAPPING (Generative VCTK) ---
# p226: Deep Male (Host Jack)
# p225: Clear Female (Host Olivia)
# p237: Distinct Male (Guest Ryan/Leo)
# p236: Distinct Female (Guest Mia/Chloe)
VOICE_MODEL_MAP = {
    # HOSTS
    "vits_male_01":   {"speaker": "p226"},
    "vits_female_01": {"speaker": "p225"},
    
    # GUESTS
    "vits_male_02":   {"speaker": "p237"},
    "vits_female_02": {"speaker": "p236"},
}

class VoiceEngine:
    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS will use device: {self.device.upper()}")
        
        # Load VCTK Model (Generative)
        self.logger.info("Initializing Coqui TTS model (vctk/vits)...")
        try:
            self.tts = TTS("tts_models/en/vctk/vits").to(self.device)
            self.logger.info("Successfully loaded VCTK VITS model.")
        except Exception as e:
            self.logger.critical(f"CRITICAL: Failed to load TTS model. Error: {e}")
            raise RuntimeError("Could not load required TTS model.") from e

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Generating audio for {len(script)} lines...")
        
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        line_audio_metadata = []
        combined_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            text = line["text"]
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                # 1. Look up character
                character = self.character_manager.get_character_by_id(speaker_id)
                voice_key = character["voice"]
                
                # 2. Determine Speaker
                if voice_key in VOICE_MODEL_MAP:
                    speaker = VOICE_MODEL_MAP[voice_key]["speaker"]
                else:
                    # Fallback (Gender Safe)
                    speaker = "p226" if character['gender'] == 'male' else "p225"
                    self.logger.warning(f"Voice key '{voice_key}' not found. Fallback to {speaker}.")

                # VISIBLE LOGGING
                self.logger.info(f"Line {i+1}: {character['name']} ({character['gender']}) -> Speaker {speaker}")

                # 3. Generate
                self.tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=str(line_filename)
                )

                segment = AudioSegment.from_wav(line_filename)
                combined_audio += segment
                line_audio_metadata.append({"path": str(line_filename), "duration": len(segment)})

            except Exception as e:
                self.logger.error(f"Error on line {i}: {e}")
                continue
        
        master_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_path, format="wav")
        return str(master_path), line_audio_metadata
