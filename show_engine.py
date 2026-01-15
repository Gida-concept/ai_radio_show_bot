"""
show_engine.py
Forces long scripts + Human-like, untitled intro.
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
        self.logger.info(f"[{show_id}] Generating LONG, NATURAL script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        prompt = f"""
        Write a radio dating show script.
        Hosts: {host_names}
        Guests: {guest_names} (Just finished a first date).

        **CRITICAL INSTRUCTION 1: NO CHEESY TITLES**
        - Do NOT say "Welcome to AI Love Connections".
        - Do NOT name the show.
        - Start **immediately** with casual, human banter between the hosts (e.g., talking about the weather, the city, the vibe of the night, or a viral topic).
        - Make it feel like the listener just tuned into a real conversation.

        **CRITICAL INSTRUCTION 2: LENGTH**
        You MUST generate a script of **AT LEAST 80 to 100 LINES**.

        **STRUCTURE:**
        1. **The Vibe Check (15 lines):** Hosts chatting casually. "Jack, have you been outside? It's pouring." "I know, Olivia, crazy night." Then they bring in the guests.
        2. **The Meet (20 lines):** How the guests met.
        3. **The Date (30 lines):** DETAILED discussion of the restaurant, food, and awkward moments.
        4. **The Verdict (15 lines):** Second date? Yes/No.
        5. **Outro (10 lines):** A cool sign-off. "Stay warm out there, Seattle."

        **OUTPUT FORMAT:**
        A single JSON array of objects. Keys: "speaker_id" (int), "text" (string), "scene" (string), "emotion" (string).
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.75, # Slightly higher for more natural flair
                max_tokens=8000,
                response_format={"type": "json_object"}, 
            )
            
            content = chat_completion.choices[0].message.content
            data = json.loads(content)
            
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
