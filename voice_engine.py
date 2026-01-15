"""
voice_engine.py
- 4 DISTINCT VOICES (p226, p225, p237, p236).
- TEXT-BASED EMOTION: Modifies text to force tone (Shouting, Stuttering, etc).
- VISIBLE LOGGING.
"""

import torch
import logging
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment

import config
from character_manager import CharacterManager

# --- VOICE MAPPING (The Working 4-Voice Set) ---
# p226: Deep Male (Host Jack)
# p225: Clear Female (Host Olivia)
# p237: Distinct Male (Guest Ryan/Leo)
# p236: High-Pitch Female (Guest Mia/Chloe)
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
        
        self.logger.info("Initializing Coqui TTS model (vctk/vits)...")
        try:
            self.tts = TTS("tts_models/en/vctk/vits").to(self.device)
            self.logger.info("Successfully loaded VCTK VITS model.")
        except Exception as e:
            self.logger.critical(f"CRITICAL: Failed to load TTS model. Error: {e}")
            raise RuntimeError("Could not load required TTS model.") from e

    def _emotionalize_text(self, text: str, emotion: str) -> str:
        """
        Rewrites text to force VITS to change tone/rhythm.
        """
        if not emotion:
            return text
        e = emotion.lower()
        
        # 1. ANGER / SHOUTING (Caps + Staccato)
        if any(x in e for x in ["angr", "yell", "shout", "furious", "mad"]):
            return text.upper().replace(" ", ". ") + "!"

        # 2. SHOCK / SURPRISE (Interrobangs)
        if any(x in e for x in ["shock", "surpris", "disbelief", "no way"]):
            return text.replace("?", "?!").replace("!", "?!") + "?!"

        # 3. NERVOUS / AWKWARD (Stuttering/Pauses)
        if any(x in e for x in ["nervous", "awkward", "hesitant", "shy"]):
            words = text.split()
            if len(words) > 3:
                mid = len(words) // 2
                words.insert(mid, "...um...")
            return "Um... " + " ".join(words) + "..."

        # 4. LAUGHING / EXCITED (Phonetics)
        if any(x in e for x in ["excit", "happy", "laugh", "funny"]):
            return text + "! Ha! Ha!"

        # 5. SARCASM (Quotes)
        if any(x in e for x in ["sarcas", "sassy"]):
            return f'"{text}"... really?'

        return text

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Generating EMOTIONAL audio for {len(script)} lines...")
        
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        line_audio_metadata = []
        combined_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            original_text = line["text"]
            emotion = line.get("emotion", "")
            
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                # 1. Resolve Speaker
                character = self.character_manager.get_character_by_id(speaker_id)
                voice_key = character["voice"]
                
                if voice_key in VOICE_MODEL_MAP:
                    speaker = VOICE_MODEL_MAP[voice_key]["speaker"]
                else:
                    speaker = "p226" if character['gender'] == 'male' else "p225"
                    self.logger.warning(f"Voice key {voice_key} not found. Fallback to {speaker}.")

                # 2. APPLY TONE (Emotionalize)
                final_text = self._emotionalize_text(original_text, emotion)

                # Log it so you can see the tone change
                self.logger.info(f"Line {i+1}: {character['name']} ({emotion}) -> {speaker}")
                if final_text != original_text:
                    self.logger.info(f"   Tone Mod: {final_text}")

                # 3. Generate
                self.tts.tts_to_file(text=final_text, speaker=speaker, file_path=str(line_filename))

                # 4. Combine
                segment = AudioSegment.from_wav(line_filename)
                combined_audio += segment

                # Save ORIGINAL text for subtitles (so captions are easy to read)
                line_audio_metadata.append({
                    "path": str(line_filename),
                    "duration_ms": len(segment),
                    "speaker_id": speaker_id,
                    "text": original_text, 
                })

            except Exception as e:
                self.logger.error(f"Error on line {i}: {e}")
                continue
        
        master_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_path, format="wav")
        return str(master_path), line_audio_metadata
