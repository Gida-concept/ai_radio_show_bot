"""
show_engine.py
Forces long scripts by demanding a 100-line output.
"""
import json
import logging
from typing import List, Dict, Any
from groq import Groq
import config
from character_manager import CharacterManager

class ShowEngine:
    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        self.client = Groq(api_key=config.GROQ_API_KEY)

    def generate_script(self, hosts: List[Dict], guests: List[Dict], show_id: str) -> List[Dict[str, Any]]:
        self.logger.info(f"[{show_id}] Generating LONG script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        # This prompt is engineered to force length by asking for specific line counts per section.
        prompt = f"""
        Write a radio dating show script for "AI Love Connections".
        Hosts: {host_names}
        Guests: {guest_names} (Just finished a first date).

        **CRITICAL INSTRUCTION: LENGTH**
        You MUST generate a script of **AT LEAST 80 to 100 LINES**.
        Do not summarize. Write every single spoken sentence.

        **STRUCTURE:**
        1. **Intro (15 lines):** Hosts introduce show, weather, vibe.
        2. **The Meet (20 lines):** Guests explain how they met and their first impressions.
        3. **The Date (30 lines):** DETAILED discussion of the restaurant, the food, the awkward moments, the conversation.
        4. **The Verdict (15 lines):** The "Will there be a second date?" moment.
        5. **Outro (10 lines):** Sign off.

        **OUTPUT FORMAT:**
        A single JSON array of objects. Keys: "speaker_id" (int), "text" (string), "scene" (string), "emotion" (string).
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.7,
                max_tokens=8000, # Maximize length
                response_format={"type": "json_object"}, 
            )
            
            content = chat_completion.choices[0].message.content
            data = json.loads(content)
            
            # Handle different JSON returns
            if isinstance(data, dict):
                key = next(iter(data))
                script = data[key]
            else:
                script = data

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script generation failed: {e}")
            raise
