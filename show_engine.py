"""
show_engine.py
- PROMPT: HIGH-OCTANE DRAMA, ROASTING, AND SHOCK VALUE.
- LENGTH: 100+ LINES (8-10 Mins).
- SAFETY: ID Fixing included.
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
        self.logger.info(f"[{show_id}] Generating HIGH-OCTANE DRAMA script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        prompt = f"""
        You are the showrunner for the most chaotic, viral dating show on the internet.
        **GOAL:** Write a script so spicy and dramatic that it gets 1 million comments.
        
        **THE CAST:**
        - Hosts ({host_names}): They are NOT polite. They roast the guests. They gasp loudly. They dig for drama.
        - Guests ({guest_names}): They just had a DISASTROUS or WILD first date.

        **CRITICAL RULES FOR EXCITEMENT:**
        1.  **NO BORING SMALL TALK.** Do not ask "How are you?" Start with a bang.
        2.  **THE "TEA":** The date cannot be normal. 
            - *Examples:* He brought a puppet? She ate off his plate without asking? He forgot his wallet? She texted her ex?
        3.  **ROASTING:** If a guest did something dumb, the hosts must call them out. "Girl, you did WHAT?!"
        4.  **ARGUMENTS:** The guests should disagree about what happened. "That is NOT how it happened!"
        5.  **LENGTH:** **100+ LINES**. Keep the drama going. Do not solve it quickly.

        **SCENE BREAKDOWN:**
        1.  **THE TEASE (20 lines):** Hosts are already laughing/screaming about the date before guests speak.
        2.  **THE CRIME (30 lines):** The specific crazy thing that happened. Extreme detail.
        3.  **THE DEFENSE (30 lines):** The other guest tries to justify their crazy behavior.
        4.  **THE VERDICT (20 lines):** The final decision. Second date? Usually NO, but make it dramatic.

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
