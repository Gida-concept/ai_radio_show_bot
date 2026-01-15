"""
voice_engine.py
STRICT GENDER ENFORCEMENT.
"""
import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment
import config
from character_manager import CharacterManager

# --- STRICT VOICE MAPPING ---
# We force ALL males to 'p226' and ALL females to 'p225'.
# There is no chance of error with this map.
VOICE_MODEL_MAP = {
    # MALE VOICES
    "vits_male_01":   {"model_name": "tts_models/en/vctk/vits", "speaker": "p226"},
    "vits_male_02":   {"model_name": "tts_models/en/vctk/vits", "speaker": "p226"},
    
    # FEMALE VOICES
    "vits_female_01": {"model_name": "tts_models/en/vctk/vits", "speaker": "p225"},
    "vits_female_02": {"model_name": "tts_models/en/vctk/vits", "speaker": "p225"},
}

class VoiceEngine:
    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS Device: {self.device}")
        
        # Load the VITS model once
        self.logger.info("Loading VCTK VITS Model...")
        self.tts = TTS("tts_models/en/vctk/vits").to(self.device)
        self.logger.info("Model Loaded.")

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
                char = self.character_manager.get_character_by_id(speaker_id)
                voice_key = char["voice"]
                
                # FORCE GENDER CHECK
                if char['gender'] == 'male':
                    speaker = 'p226' # Always Male
                else:
                    speaker = 'p225' # Always Female
                
                self.logger.info(f"Line {i}: {char['name']} ({char['gender']}) -> Speaker {speaker}")

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
