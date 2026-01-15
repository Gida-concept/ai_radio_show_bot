"""
voice_engine.py
4 DISTINCT VOICES (2 MALE, 2 FEMALE).
"""
import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment
import config
from character_manager import CharacterManager

# --- VOICE MAPPING ---
# Hosts use the voices you liked. Guests use NEW, distinct voices.
VOICE_MODEL_MAP = {
    # HOSTS
    "vits_male_01":   {"speaker": "p226"}, # Jack (Deep Male - Original)
    "vits_female_01": {"speaker": "p225"}, # Olivia (Clear Female - Original)
    
    # GUESTS (New Voices)
    "vits_male_02":   {"speaker": "p232"}, # Ryan/Leo (Distinct Masculine)
    "vits_female_02": {"speaker": "p228"}, # Mia/Chloe (Distinct Feminine)
}

class VoiceEngine:
    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS Device: {self.device}")
        
        # Load the VCTK Model
        self.logger.info("Loading VCTK VITS Model...")
        self.tts = TTS("tts_models/en/vctk/vits").to(self.device)
        self.logger.info("Model Loaded.")

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Generating audio for {len(script)} lines...")
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        combined_audio = AudioSegment.silent(duration=0)
        line_audio_metadata = []

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            text = line["text"]
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                # 1. Get Character
                char = self.character_manager.get_character_by_id(speaker_id)
                voice_key = char["voice"] # e.g., "vits_male_02"
                
                # 2. Get Speaker ID from Map
                if voice_key in VOICE_MODEL_MAP:
                    speaker = VOICE_MODEL_MAP[voice_key]["speaker"]
                else:
                    # Fallback if config is wrong, but maintain gender
                    speaker = "p226" if char['gender'] == 'male' else "p225"
                    self.logger.warning(f"Voice key {voice_key} not found. Fallback to {speaker}")

                self.logger.debug(f"Line {i}: {char['name']} -> {speaker}")

                # 3. Generate
                self.tts.tts_to_file(text=text, speaker=speaker, file_path=str(line_filename))

                segment = AudioSegment.from_wav(line_filename)
                combined_audio += segment
                line_audio_metadata.append({"path": str(line_filename), "duration": len(segment)})

            except Exception as e:
                self.logger.error(f"Error on line {i}: {e}")
                continue
        
        master_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_path, format="wav")
        return str(master_path), line_audio_metadata
