"""
show_engine.py

Responsible for generating the show's script using the Groq LLM.
- Constructs a detailed prompt for the LLM.
- Interacts with the Groq API to get the script.
- Validates and parses the LLM's JSON output.
"""

import json
import logging
import random
from typing import List, Dict, Any

from groq import Groq

import config
from character_manager import CharacterManager


class ShowEngine:
    """Generates the conversational script for the dating show."""

    def __init__(self, character_manager: CharacterManager):
        """
        Initializes the ShowEngine.

        Args:
            character_manager (CharacterManager): An instance for accessing character data.
        """
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
        """
        Builds the detailed prompt for the Groq LLM to generate the script.

        Args:
            hosts (List[Dict]): A list of host character dictionaries.
            guests (List[Dict]): A list of guest character dictionaries.

        Returns:
            str: The fully constructed prompt string.
        """
        host_names = " and ".join([h['name'] for h in hosts])
        guest_names = " and ".join([g['name'] for g in guests])

        characters_description = "\n".join(
            f"- {char['name']} (ID: {char['id']}, Gender: {char['gender']}): {char['persona']}"
            for char in hosts + guests
        )

        show_duration = random.randint(config.MIN_SHOW_DURATION_MINUTES, config.MAX_SHOW_DURATION_MINUTES)

        # Using a f-string with triple quotes for a clean, multi-line prompt template.
        prompt = f"""
        You are an AI scriptwriter for a 24/7 fully autonomous radio dating show.
        Your task is to generate a realistic, engaging, and unpredictable conversation script.

        **SHOW DETAILS:**
        - Title: AI Love Connections
        - Hosts: {host_names}
        - Guests: {guest_names}, who have just been on a first date.
        - Target Duration: Approximately {show_duration} minutes of spoken content.

        **CHARACTERS:**
        {characters_description}

        **SCRIPTING RULES (ABSOLUTE):**
        1.  **FORMAT:** You MUST output a valid JSON array. Each element in the array is a JSON object representing one line of dialogue. Each object MUST have these exact keys: "speaker_id", "text", "scene", "emotion".
        2.  **JSON ONLY:** Your entire response must be a single JSON array, starting with `[` and ending with `]`. Do NOT include any text, explanations, or markdown formatting before or after the JSON.
        3.  **CONVERSATION FLOW:**
            - The conversation must feel natural, like a real radio show. Use filler words (uh, um, you know), laughter, and interruptions.
            - Hosts should drive the conversation, asking the guests about their date.
            - Guests should recount their date experience, which could have happened at a real-world location (e.g., a specific restaurant, park, cinema).
            - Include moments of humor, awkwardness, connection, and disagreement.
            - Hosts can interrupt each other or the guests to add commentary.
        4.  **ENDING:**
            - Towards the end, the hosts MUST ask the guests if they want a second date.
            - If YES: They should decide on a real, specific activity and location for the second date (e.g., "Let's try that Italian place in Greenwich Village next Friday night").
            - If NO: The hosts should try to understand why, perhaps gently challenge their reasoning, and then wrap up the segment gracefully for the audience.
        5.  **CONTENT:**
            - "speaker_id" must be an integer corresponding to the character IDs provided.
            - "text" should be the spoken dialogue.
            - "scene" should describe the location being discussed (e.g., "cinema lobby", "restaurant patio", "park bench"). It can change as they recount different parts of their date.
            - "emotion" should be a single word describing the speaker's tone (e.g., "curious", "laughing", "nervous", "excited", "disappointed").

        **EXAMPLE OF A SINGLE LINE:**
        {{
          "speaker_id": 1,
          "text": "So, Ryan, Mia tells me you picked the movie. Was it a good choice?",
          "scene": "recounting the date",
          "emotion": "teasing"
        }}

        Now, generate the complete script as a single JSON array.
        """
        return prompt

    def generate_script(self, hosts: List[Dict], guests: List[Dict], show_id: str) -> List[Dict[str, Any]]:
        """
        Calls the Groq LLM to generate the script and validates the output.

        Args:
            hosts (List[Dict]): The selected host characters.
            guests (List[Dict]): The selected guest characters.
            show_id (str): The unique identifier for the current show.

        Returns:
            List[Dict[str, Any]]: A validated list of script line objects.

        Raises:
            ValueError: If the LLM output is not valid JSON or doesn't match the required format.
        """
        self.logger.info(f"[{show_id}] Constructing prompt and generating script...")
        prompt = self._construct_prompt(hosts, guests)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.8,  # Higher temp for more creative, less predictable conversation
                max_tokens=8000,
                response_format={"type": "json_object"},  # Enforce JSON output
            )

            response_content = chat_completion.choices[0].message.content
            self.logger.info(f"[{show_id}] Successfully received script from Groq LLM.")
            self.logger.debug(f"[{show_id}] Raw LLM Output: {response_content[:500]}...")  # Log a snippet

            # The LLM is instructed to return a JSON array, but the `json_object` type
            # might wrap it in a root object. We need to handle this.
            parsed_json = json.loads(response_content)

            # Check if the response is a dict with a single key that is an array
            if isinstance(parsed_json, dict) and len(parsed_json) == 1:
                key = next(iter(parsed_json))
                if isinstance(parsed_json[key], list):
                    script_data = parsed_json[key]
                else:
                    raise ValueError("JSON object from LLM does not contain a list as its value.")
            elif isinstance(parsed_json, list):
                script_data = parsed_json
            else:
                raise ValueError("Parsed JSON from LLM is not a list or a dictionary containing a single list.")

            # Final validation of the script structure
            self._validate_script(script_data, hosts + guests)
            self.logger.info(f"[{show_id}] Script parsed and validated successfully. Total lines: {len(script_data)}")
            return script_data

        except json.JSONDecodeError as e:
            self.logger.error(f"[{show_id}] FAILED to parse JSON from LLM response. Error: {e}")
            self.logger.error(
                f"Response snippet: {response_content[:500] if 'response_content' in locals() else 'N/A'}")
            raise ValueError("LLM response was not valid JSON.") from e
        except Exception as e:
            self.logger.critical(f"[{show_id}] An unexpected error occurred during script generation: {e}")
            raise

    def _validate_script(self, script: List[Dict], characters: List[Dict]):
        """Performs a basic validation on the structure of the generated script."""
        if not isinstance(script, list) or not script:
            raise ValueError("Script is not a non-empty list.")

        valid_speaker_ids = {char['id'] for char in characters}
        required_keys = {"speaker_id", "text", "scene", "emotion"}

        for i, line in enumerate(script):
            if not isinstance(line, dict):
                raise ValueError(f"Script line {i + 1} is not a dictionary.")
            if not required_keys.issubset(line.keys()):
                raise ValueError(f"Script line {i + 1} is missing required keys.")
            if line['speaker_id'] not in valid_speaker_ids:
                raise ValueError(f"Script line {i + 1} has an invalid speaker_id: {line['speaker_id']}.")