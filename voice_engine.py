"""
voice_engine.py
- SIMPLE, ROBUST 2-VOICE SYSTEM.
- Male = p226 (Deep)
- Female = p225 (Clear)
- Works perfectly for 1-on-1 Mixed Gender interviews.
"""

import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment
import config
from character_manager import CharacterManager

class VoiceEngine:
    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"TTS Device: {self.device}")
        
        self.logger.info("Loading VCTK Model...")
        self.tts = TTS("tts_models/en/vctk/vits").to(self.device)

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Generating audio...")
        
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        combined_audio = AudioSegment.silent(duration=0)
        line_metadata = []

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            text = line["text"]
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                char = self.character_manager.get_character_by_id(speaker_id)
                
                # SUPER SIMPLE LOGIC:
                if char['gender'] == 'male':
                    speaker = "p226"
                else:
                    speaker = "p225"

                self.logger.info(f"Line {i+1}: {char['name']} ({char['gender']}) -> {speaker}")

                self.tts.tts_to_file(text=text, speaker=speaker, file_path=str(line_filename))

                segment = AudioSegment.from_wav(line_filename)
                combined_audio += segment
                line_metadata.append({"path": str(line_filename), "duration": len(segment), "text": text, "speaker_id": speaker_id})

            except Exception as e:
                self.logger.error(f"Error line {i}: {e}")
                continue
        
        master_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_path, format="wav")
        return str(master_path), line_metadata
