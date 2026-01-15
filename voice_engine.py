"""
voice_engine.py

Handles TTS operations with TEXT-BASED EMOTION ENGINEERING.
- Preserves 4-Voice Logic (p226, p225, p237, p236).
- Modifies text punctuation/caps based on 'emotion' tag to force prosody changes.
"""

import torch
import logging
import random
from typing import List, Dict, Any, Tuple
from TTS.api import TTS
from pydub import AudioSegment

import config
from character_manager import CharacterManager

# --- VOICE MAPPING (UNCHANGED) ---
# p226: Deep Male (Host Jack)
# p225: Clear Female (Host Olivia)
# p237: Distinct Male (Guest Ryan/Leo)
# p236: Distinct Female (Guest Mia/Chloe)
VOICE_MODEL_MAP = {
    "vits_male_01":   {"speaker": "p226"},
    "vits_female_01": {"speaker": "p225"},
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
        Rewrites text to force VITS to change tone/rhythm based on emotion.
        """
        if not emotion:
            return text
            
        e = emotion.lower()
        
        # 1. ANGER / YELLING / SHOUTING
        # Effect: CAPS lock + periods for staccato rhythm
        if any(x in e for x in ["angr", "yell", "shout", "furious", "mad"]):
            # "Stop it now" -> "STOP. IT. NOW!"
            return text.upper().replace(" ", ". ") + "!"

        # 2. SHOCK / SURPRISE / DISBELIEF
        # Effect: CAPS on key words + Interrobangs (?!)
        if any(x in e for x in ["shock", "surpris", "disbelief", "no way", "what"]):
            # "No way did he say that" -> "NO WAY?! Did he say that?!"
            return text.replace("?", "?!").replace("!", "?!") + "?!"

        # 3. NERVOUS / AWKWARD / HESITANT
        # Effect: Insert "um", "uh", and ellipses "..." for pauses
        if any(x in e for x in ["nervous", "awkward", "hesitant", "shy", "uncomfortable"]):
            # "I think so" -> "I... um... I think... so..."
            words = text.split()
            if len(words) > 3:
                mid = len(words) // 2
                words.insert(mid, "...um...")
            return "Um... " + " ".join(words) + "..."

        # 4. EXCITED / HAPPY / LAUGHING
        # Effect: Exclamation marks + "Haha" phonetics
        if any(x in e for x in ["excit", "happy", "laugh", "funny", "lol"]):
            # "That is so funny" -> "That is SO funny! Ha! Ha!"
            return text + "! Ha! Ha!"

        # 5. SARCASM / SASSY
        # Effect: Quotation marks + specific emphasis
        if any(x in e for x in ["sarcas", "sassy", "ironic"]):
            return f'"{text}"... really?'

        # Default: Just return text as is
        return text

    def generate_show_audio(self, script: List[Dict[str, Any]], show_id: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.logger.info(f"[{show_id}] Starting audio generation for {len(script)} script lines.")
        
        show_audio_dir = config.AUDIO_DIR / show_id
        show_audio_dir.mkdir(parents=True, exist_ok=True)
        
        line_audio_metadata = []
        combined_audio = AudioSegment.silent(duration=0)

        for i, line in enumerate(script):
            speaker_id = line["speaker_id"]
            original_text = line["text"]
            emotion = line.get("emotion", "") # Get emotion from script
            
            line_filename = show_audio_dir / f"line_{i:03d}_{speaker_id}.wav"

            try:
                # 1. Resolve Speaker (Standard Logic)
                character = self.character_manager.get_character_by_id(speaker_id)
                voice_key = character["voice"]
                
                if voice_key in VOICE_MODEL_MAP:
                    speaker = VOICE_MODEL_MAP[voice_key]["speaker"]
                else:
                    speaker = "p226" if character['gender'] == 'male' else "p225"
                    self.logger.warning(f"Voice key '{voice_key}' not found. Fallback to {speaker}.")

                # 2. EMOTIONALIZE TEXT
                # We transform the text before sending it to the AI
                final_text = self._emotionalize_text(original_text, emotion)

                # Log visible confirmation
                self.logger.info(f"Line {i+1}: {character['name']} ({emotion}) -> {speaker}")
                if final_text != original_text:
                    self.logger.debug(f"   Original: {original_text}")
                    self.logger.debug(f"   Modified: {final_text}")

                # 3. Generate Audio
                self.tts.tts_to_file(
                    text=final_text,
                    speaker=speaker,
                    file_path=str(line_filename)
                )

                # 4. Combine
                line_audio = AudioSegment.from_wav(line_filename)
                combined_audio += line_audio

                line_audio_metadata.append({
                    "path": str(line_filename),
                    "duration_ms": len(line_audio),
                    "speaker_id": speaker_id,
                    "text": original_text, # Save original text for subtitles!
                })

            except Exception as e:
                self.logger.error(f"Failed to generate audio for line {i}: '{original_text}'. Error: {e}")
                continue
        
        master_audio_path = config.AUDIO_DIR / f"master_audio_{show_id}.wav"
        combined_audio.export(master_audio_path, format="wav")
        return str(master_audio_path), line_audio_metadata
