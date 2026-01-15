"""
show_engine.py
- VIRAL/ENGAGING PROMPT (Drama, Humor).
- SAFETY LAYER (Fixes Name vs ID errors).
- ENFORCES EXTREME LENGTH (100+ lines) by mandating section lengths.
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
        Do not summarize. Do not rush. You must write out every single awkward pause and argument.

        **REQUIRED SCENE BREAKDOWN (Follow this exactly to get length):**
        1.  **THE HOOK (20 Lines):** 
            - Start mid-conversation about a viral topic or the weather. 
            - Then tease the date: "Folks, you are not going to believe what happened at Olive Garden tonight."
        2.  **THE MEET CUTE (20 Lines):** 
            - How did they meet? (Tinder? A bar?). 
            - First impressions (Was he shorter than his profile? Did she look like her photos?).
        3.  **THE DATE DISASTER (40 Lines):** 
            - **This is the main event.** Go into extreme detail.
            - What did they eat? (Describe the smell/taste).
            - What went wrong? (Rude waiter? Ex-girlfriend showed up? Spilled drink?).
            - Hosts must interrupt constantly with reactions ("NO WAY!", "Stop it!").
        4.  **THE VERDICT (20 Lines):** 
            - The debate. Hosts take sides.
            - The final question: Second Date? Yes or No.
            - The outro.

        **STYLE GUIDE:**
        - Make it messy and real. Use slang. Use interruptions.
        - **NO "Welcome to..." intros.**
        - **NO cheesy radio voices.** Talk like real people on a podcast.

        **OUTPUT FORMAT:**
        A single JSON array. Keys: "speaker_id", "text", "scene", "emotion".
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.85, # High creativity/volatility
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
            
            # Warn if it's still short (shouldn't happen with this prompt)
            if len(script) < 80:
                self.logger.warning(f"Script is shorter than requested ({len(script)} lines).")

            return script

        except Exception as e:
            self.logger.critical(f"Script generation failed: {e}")
            raise
