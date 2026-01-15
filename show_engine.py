"""
show_engine.py
Logic: Unchanged.
Prompt: OPTIMIZED FOR FACEBOOK ENGAGEMENT (Drama, Humor, Awkwardness, Realism).
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
        You are the head writer for a viral, high-energy dating show that airs on Facebook Watch.
        **Goal:** Create a script so funny, awkward, and engaging that people CANNOT stop listening.

        **THE CAST:**
        Hosts: {host_names} (They are messy, opinionated, and love gossip).
        Guests: {guest_names} (Just finished a first date).

        **CRITICAL INSTRUCTIONS FOR "FACEBOOK ENGAGEMENT":**
        1.  **NO ROBOTIC INTROS:** Start mid-conversation. Start with energy. "Okay, stop, stop. You said he wore WHAT?"
        2.  **CREATE TENSION:** We need disagreements. 
            - Example: "Wait, you split the bill on a first date? In 2024??" 
            - Example: "He talked about his crypto portfolio for 20 minutes?"
        3.  **MAKE IT AWKWARD:** Include moments where one guest says something cringe, and the others react (silence, nervous laughter).
        4.  **SENSORY DETAILS:** Don't say "The food was bad." Say "The sushi smelled like wet socks and the rice was crunchy."
        5.  **HOSTS MUST REACT:** The hosts are the audience surrogates. They should gasp, laugh loud, take sides, and "stir the pot."

        **LENGTH REQUIREMENT:**
        - **80 to 120 LINES.** (Approx 8-10 minutes).
        - Do not rush. Milk the drama.

        **SCRIPT STRUCTURE:**
        1.  **The Hook (Min 0-1):** Hosts teasing the audience. "We have a wild one tonight folks."
        2.  **The Backstory (Min 1-3):** How they met. Was it a catfish situation? A drunk DM?
        3.  **The Date Disaster/Triumph (Min 3-6):** Specifics. The waiter was rude. The ex-girlfriend showed up. The food was inedible. 
        4.  **The "Hot Take" Debate (Min 6-7):** Hosts and guests argue about a dating rule (e.g., splitting the bill, kissing on first date). **This drives comments.**
        5.  **The Verdict (Min 7-8+):** High suspense. Will they go out again?
            - If NO: The rejection must be brutal but funny.
            - If YES: It must be cute and specific.

        **OUTPUT FORMAT:**
        A single JSON array. Keys: "speaker_id", "text", "scene", "emotion".
        Use "emotion" to guide the voice (e.g., "shocked", "wheezing laughter", "defensive", "flirty").

        WRITE THE SCRIPT NOW. MAKE IT SPICY.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.8, # High temp for maximum personality
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
