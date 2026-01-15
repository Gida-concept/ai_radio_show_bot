"""
show_engine.py
- VIRAL/ENGAGING PROMPT.
- ENFORCES EXTREME LENGTH (100+ lines).
- SAFETY LAYER (Fixes Name vs ID errors).
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
        self.logger.info(f"[{show_id}] Generating LONG VIRAL script...")
        
        host_names = ", ".join([h['name'] for h in hosts])
        guest_names = ", ".join([g['name'] for g in guests])
        
        prompt = f"""
        You are the head writer for a viral Facebook Watch dating show.
        **GOAL:** Generate a massive, detailed script (8-10 minutes spoken time).

        **THE CAST:**
        Hosts: {host_names} (Gossipy, funny, opinionated).
        Guests: {guest_names} (Just finished a first date).

        **MANDATORY LENGTH INSTRUCTIONS:**
        You MUST generate a JSON array containing **AT LEAST 100 OBJECTS (Lines of dialogue)**.
        Do not summarize. Write out every single awkward pause and argument.

        **REQUIRED SCENE BREAKDOWN:**
        1.  **THE HOOK (20 Lines):** Start mid-conversation. High energy. Tease the drama.
        2.  **THE MEET CUTE (20 Lines):** First impressions. Be specific.
        3.  **THE DATE DISASTER (40 Lines):** **Main Event.** Sensory details (smells, tastes). rude waiters, spilled drinks.
        4.  **THE VERDICT (20 Lines):** The debate. The final decision (Yes/No).

        **STYLE GUIDE:**
        - Make it messy and real. Use slang.
        - **NO "Welcome to..." intros.**
        - **NO cheesy radio voices.**

        **OUTPUT FORMAT:**
        A single JSON array. Keys: "speaker_id", "text", "scene", "emotion".
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.85, # High creativity
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
            name_map = {c['name']: c['id'] for c in hosts + guests}
            cleaned_script = []
            for line in script:
                sid = line.get('speaker_id')
                # If sid is a Name string, convert to ID
                if isinstance(sid, str):
                    if sid in name_map:
                        line['speaker_id'] = name_map[sid]
                        cleaned_script.append(line)
                elif isinstance(sid, int):
                    cleaned_script.append(line)
            script = cleaned_script
            # -------------------------------------

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script generation failed: {e}")
            raise
