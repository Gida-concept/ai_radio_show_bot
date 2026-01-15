"""
show_engine.py
- VIRAL/ENGAGING PROMPT (Drama, Humor).
- SAFETY LAYER: Automatically fixes Name vs ID errors.
- ENFORCES LENGTH (80+ lines).
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
        self.logger.info(f"[{show_id}] Generating VIRAL/ENGAGING script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        prompt = f"""
        You are the head writer for a viral, high-energy dating show on Facebook Watch.
        **Goal:** Create a script so funny, awkward, and engaging that listeners comment immediately.

        **THE CAST:**
        Hosts: {host_names} (Messy, opinionated, love gossip).
        Guests: {guest_names} (Just finished a first date).

        **INSTRUCTIONS:**
        1.  **START HOT:** No "Welcome to...". Start mid-argument or mid-laugh.
        2.  **CREATE TENSION:** Disagreements about who paid, rude waiters, or awkward silences.
        3.  **SENSORY DETAILS:** "The sushi smelled like wet socks."
        4.  **LENGTH:** **80 to 100 LINES**. Do not summarize. Write every dialogue line.

        **STRUCTURE:**
        1.  **The Hook (Min 0-1):** Hosts teasing the audience/guests.
        2.  **The Backstory (Min 1-3):** How they met (Tinder nightmare?).
        3.  **The Date (Min 3-6):** The disaster details.
        4.  **The Debate (Min 6-7):** Hosts take sides. "Jack, you can't say that!"
        5.  **The Verdict (Min 7+):** Second date? Yes/No.

        **OUTPUT FORMAT:**
        A single JSON array. Keys: "speaker_id", "text", "scene", "emotion".
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.8,
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

            # --- SAFETY LAYER: Fix Speaker IDs ---
            # If the AI put "Jack" instead of ID 1, we fix it here.
            name_map = {c['name']: c['id'] for c in hosts + guests}
            
            cleaned_script = []
            for line in script:
                sid = line.get('speaker_id')
                
                # If sid is a Name string, convert to ID
                if isinstance(sid, str):
                    if sid in name_map:
                        line['speaker_id'] = name_map[sid]
                        cleaned_script.append(line)
                    else:
                        self.logger.warning(f"Skipping line with unknown speaker name: {sid}")
                # If sid is already an Int, keep it
                elif isinstance(sid, int):
                    cleaned_script.append(line)
            
            script = cleaned_script
            # -------------------------------------

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script generation failed: {e}")
            raise
