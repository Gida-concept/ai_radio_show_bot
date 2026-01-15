"""
show_engine.py
- FORMAT: 1-on-1 Intimate Interview.
- TONE: Realistic, Spicy, Emotional.
- LENGTH: EXTENDED (130+ Lines).
- INCLUDES: Social Media Call-To-Action (Share/Like/Comment).
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
        self.logger.info(f"[{show_id}] Generating EXTENDED INTERVIEW script...")
        
        host = hosts[0]
        guest = guests[0]
        
        prompt = f"""
        You are writing a script for "The Ex-Files," a raw, intimate radio interview show about heartbreak and relationships.
        
        **THE HOST:** {host['name']} ({host['gender']}). Empathetic but pries for details. Wants the truth.
        **THE GUEST:** {guest['name']} ({guest['gender']}). **Scenario:** {guest['persona']}
        
        **GOAL:** Create a deep, emotional dive. Make it feel like a therapy session mixed with a viral confession.

        **STRUCTURE (Mandatory 135+ Lines):**
        1.  **THE WARM UP (15 lines):** Host welcomes guest. "You look tired. Drink some water." Guest is nervous. Establish the vibe.
        2.  **THE RELATIONSHIP (35 lines):** How was it at the start? "He was perfect." "She was my soulmate." The good times before the storm.
        3.  **THE BETRAYAL (45 lines):** **The Spicy Part.** How did it go wrong? 
            - Ask about the sex (keep it PG-13 but real). "Was the chemistry gone?"
            - Ask about the moment they knew it was over.
            - Ask about the cheating/lying/discovery.
        4.  **THE COMPARISON (25 lines):** "Is the new person better?" Be brutal. Compare them directly.
        5.  **THE HEALING (10 lines):** Do they still love the ex? Are they moving on?
        6.  **THE OUTRO (10 lines - CRITICAL):** The Host turns to the audience for a graceful close.
            - "Thank you listeners for joining us."
            - **Call to Action:** "If you enjoyed this story, please **SHARE** this video."
            - **Engagement:** "Have you ever been in this situation? **COMMENT** below, we want to hear YOUR story."
            - "Don't forget to **FOLLOW** and **LIKE** for more episodes."

        **STYLE:**
        - Hesitant speech ("I... I don't know").
        - Interruptions.
        - Emotional outbursts ("Don't look at me like that!").
        - **NO "Welcome to the show."** Start mid-conversation or with a mood check.

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

            # ID Fixer (Safety Layer)
            name_map = {host['name']: host['id'], guest['name']: guest['id']}
            for line in script:
                # If speaker is a name string, convert to ID
                if isinstance(line.get('speaker_id'), str):
                    line['speaker_id'] = name_map.get(line['speaker_id'], host['id'])

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script error: {e}")
            raise
