"""
show_engine.py

Responsible for generating the show's script using the Groq LLM.
- STRICTLY ENFORCES LONG-FORM CONTENT (8+ Minutes).
- ENFORCES HYPER-REALISTIC SETTINGS AND DETAILS.
"""

import json
import logging
from typing import List, Dict, Any

from groq import Groq

import config
from character_manager import CharacterManager

class ShowEngine:
    """Generates the conversational script for the dating show."""

    def __init__(self, character_manager: CharacterManager):
        self.logger = logging.getLogger(__name__)
        self.character_manager = character_manager
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in configuration.")
        
        try:
            self.client = Groq(api_key=config.GROQ_API_KEY)
            self.logger.info("Groq client initialized successfully for LLM.")
        except Exception as e:
            self.logger.critical(f"Failed to initialize Groq client: {e}")
            raise

    def _construct_prompt(self, hosts: List[Dict], guests: List[Dict]) -> str:
        host_names = " and ".join([h['name'] for h in hosts])
        guest_names = " and ".join([g['name'] for g in guests])
        
        characters_description = "\n".join(
            f"- {char['name']} (ID: {char['id']}, Gender: {char['gender']}): {char['persona']}"
            for char in hosts + guests
        )

        # THE HYPER-REALISM MEGA-PROMPT
        prompt = f"""
        You are the lead scriptwriter for "AI Love Connections", a popular, gritty, and realistic radio dating show.
        
        **OBJECTIVE:** 
        Generate a VERY LONG, detailed script (8-10 minutes spoken).
        **Target Length:** 100 to 130 lines of dialogue.
        
        **CAST:**
        Hosts: {host_names}
        Guests: {guest_names} (They just finished a first date).
        
        **CHARACTER PROFILES:**
        {characters_description}

        **REALISM GUIDELINES (CRITICAL):**
        1.  **SPECIFICITY:** Do not use generic locations. Pick a real city (e.g., NYC, London, Chicago). Name the restaurant/bar/park (e.g., "The Spotted Pig in the Village" or "Hyde Park near the fountains").
        2.  **SENSORY DETAILS:** Describe the atmosphere. Was the music too loud? Did the food taste salty? Was it raining? Did the waiter say something weird?
        3.  **IMPERFECTIONS:** Real dates are rarely perfect. Include awkward moments, misunderstandings, checking phones, or spilling drinks. 
        4.  **HUMAN SPEECH:** People use filler words ("like," "um," "literally"). They interrupt. They laugh at bad jokes. Capture this vibe.

        **MANDATORY SHOW STRUCTURE:**
        1.  **THE INTRO (Minutes 0-1):** Hosts introduce the show with high energy. Establish the city vibe (e.g., "It's a rainy night here in Seattle...").
        2.  **THE BACKSTORY (Minutes 1-3):** How did they meet? (Tinder? Hinge? A mutual friend named Sarah?). Where exactly did they go tonight? 
        3.  **THE DATE AUTOPSY (Minutes 3-6):** The deep dive. 
            - Host: "So, Ryan, be honest, did she look like her profile picture?"
            - Guest: Describe the food/drinks in detail.
            - **Conflict/Connection:** Was there a spark or a red flag? Discuss it.
        4.  **THE VERDICT PREP (Minutes 6-7):** The end of the night. The bill moment (Who paid? Was it awkward?). The goodbye (Hug? Handshake? Kiss?).
        5.  **THE FINAL DECISION (Minutes 7-8+):** 
            - Hosts force the question: "Second Date: Yes or No?"
            - If YES: Plan the *exact* next date (e.g., "Mini-golf at Chelsea Piers next Tuesday").
            - If NO: Be honest about why (e.g., "He talked about his ex too much").

        **FORMATTING RULES:**
        1.  **JSON ONLY:** Output a single JSON array containing objects.
        2.  **KEYS:** "speaker_id" (int), "text" (string), "scene" (string), "emotion" (string).
        
        GENERATE THE FULL, REALISTIC SCRIPT NOW.
        """
        return prompt

    def generate_script(self, hosts: List[Dict], guests: List[Dict], show_id: str) -> List[Dict[str, Any]]:
        self.logger.info(f"[{show_id}] Constructing prompt and generating script...")
        prompt = self._construct_prompt(hosts, guests)
        
        try:
            # High max_tokens to allow for the long script
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.8, # Higher temperature for more "messy/creative" results
                max_tokens=8000,
                response_format={"type": "json_object"}, 
            )
            
            response_content = chat_completion.choices[0].message.content
            self.logger.info(f"[{show_id}] Successfully received script from Groq LLM.")
            
            parsed_json = json.loads(response_content)

            if isinstance(parsed_json, dict) and len(parsed_json) == 1:
                key = next(iter(parsed_json))
                if isinstance(parsed_json[key], list):
                    script_data = parsed_json[key]
                else:
                    raise ValueError("JSON object from LLM does not contain a list.")
            elif isinstance(parsed_json, list):
                script_data = parsed_json
            else:
                raise ValueError("Invalid JSON format.")

            self._validate_script(script_data, hosts + guests)
            self.logger.info(f"[{show_id}] Script parsed. Total lines: {len(script_data)}")
            
            if len(script_data) < 60:
                self.logger.warning(f"[{show_id}] Script is too short ({len(script_data)} lines).")
            
            return script_data

        except Exception as e:
            self.logger.critical(f"[{show_id}] Error in script generation: {e}")
            raise

    def _validate_script(self, script: List[Dict], characters: List[Dict]):
        if not isinstance(script, list) or not script:
            raise ValueError("Script is not a list.")
        valid_speaker_ids = {char['id'] for char in characters}
        required = {"speaker_id", "text", "scene", "emotion"}
        for line in script:
            if not required.issubset(line.keys()) or line['speaker_id'] not in valid_speaker_ids:
                raise ValueError("Invalid script line format.")
