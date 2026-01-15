"""
show_engine.py
- PROMPT: MAX SPICE, TEA, AND DRAMA.
- STRUCTURE: Tease -> Crime -> Defense -> Verdict.
- LENGTH: 100+ Lines (Mandatory).
- SAFETY: ID Fixing.
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
        self.logger.info(f"[{show_id}] Generating SPICY DRAMA script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        prompt = f"""
        You are the showrunner for the most chaotic, viral dating show on the internet.
        **GOAL:** Write a script so spicy and dramatic that it gets 1 million comments.
        
        **THE CAST:**
        - Hosts ({host_names}): Messy, loud, opinionated. They LIVE for drama.
        - Guests ({guest_names}): Just had a NIGHTMARE first date.

        **MANDATORY "SPICE" INSTRUCTIONS:**
        1.  **THE TEASE (Lines 1-20):** 
            - Start mid-argument. The hosts are already shocked.
            - "I cannot believe he did that." "She is delusional!"
            - Tease the audience before introducing the guests.
        2.  **THE CRIME (Lines 21-50):** 
            - One guest accuses the other of something WILD.
            - Examples: "He brought his mom," "She texted her ex," "He ordered for me," "She stole the silverware."
            - **Be specific.** Describe the restaurant, the smell, the awkward silence.
        3.  **THE DEFENSE (Lines 51-80):** 
            - The accused guest gets ANGRY and defends themselves.
            - "You are lying!" "That is NOT what happened!"
            - The hosts take sides and roast them.
        4.  **THE VERDICT (Lines 81-100+):** 
            - The final decision. Second date? 
            - Usually "Absolutely Not," but make them fight about it.

        **LENGTH RULE:**
        - **AT LEAST 100 LINES.** Do not rush the drama. Milk every awkward moment.

        **OUTPUT FORMAT:**
        A single JSON array. Keys: "speaker_id", "text", "scene", "emotion".
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.9, # Max creativity/chaos
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

            # --- SAFETY LAYER ---
            name_map = {c['name']: c['id'] for c in hosts + guests}
            cleaned_script = []
            for line in script:
                sid = line.get('speaker_id')
                if isinstance(sid, str) and sid in name_map:
                    line['speaker_id'] = name_map[sid]
                    cleaned_script.append(line)
                elif isinstance(sid, int):
                    cleaned_script.append(line)
            script = cleaned_script
            # --------------------

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script generation failed: {e}")
            raise
