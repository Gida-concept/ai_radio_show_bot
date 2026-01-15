"""
show_engine.py
- FORMAT: 1-on-1 Intimate Interview.
- TONE: Realistic, Spicy, Emotional.
- LENGTH: 100+ Lines.
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
        self.logger.info(f"[{show_id}] Generating INTERVIEW script...")
        
        host = hosts[0]
        guest = guests[0]
        
        prompt = f"""
        You are writing a script for "The Ex-Files," a raw, intimate radio interview show about heartbreak and relationships.
        
        **THE HOST:** {host['name']} ({host['gender']}). Empathetic but pries for details. Wants the truth.
        **THE GUEST:** {guest['name']} ({guest['gender']}). **Scenario:** {guest['persona']}
        
        **GOAL:** Create a 10-minute deep dive. Make it feel like a therapy session mixed with a confession.

        **STRUCTURE (Mandatory 100+ Lines):**
        1.  **THE WARM UP (10 lines):** Host welcomes guest. "You look tired. Drink some water." Guest is nervous.
        2.  **THE RELATIONSHIP (30 lines):** How was it at the start? "He was perfect." "She was my soulmate."
        3.  **THE BETRAYAL (40 lines):** **The Spicy Part.** How did it go wrong? 
            - Ask about the sex (keep it PG-13 but real). "Was the chemistry gone?"
            - Ask about the moment they knew it was over.
            - Ask about the cheating/lying.
        4.  **THE COMPARISON (20 lines):** "Is the new person better?" Be brutal.
        5.  **THE FINAL WORD (10 lines):** Do they still love the ex?

        **STYLE:**
        - Hesitant speech ("I... I don't know").
        - Interruptions.
        - Emotional outbursts ("Don't look at me like that!").
        - **NO "Welcome to the show."** Start with the vibe check.

        **OUTPUT:** JSON Array of objects {{"speaker_id": int, "text": string}}.
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

            # ID Fixer
            name_map = {host['name']: host['id'], guest['name']: guest['id']}
            for line in script:
                if isinstance(line.get('speaker_id'), str):
                    line['speaker_id'] = name_map.get(line['speaker_id'], host['id'])

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script error: {e}")
            raise
