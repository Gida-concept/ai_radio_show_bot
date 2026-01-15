"""
character_manager.py

Manages the loading, validation, and selection of characters for the radio show.
- Loads characters from data/characters.json.
- Validates character data against configuration.
- Selects hosts and guests for each new show.
"""

import json
import random
import logging
from typing import List, Dict, Any

import config


class CharacterManager:
    """Handles all operations related to show characters."""

    def __init__(self):
        """Initializes the CharacterManager, loading and validating characters."""
        self.logger = logging.getLogger(__name__)
        self.all_characters: List[Dict[str, Any]] = self._load_characters()
        self.characters_by_id: Dict[int, Dict[str, Any]] = {
            char['id']: char for char in self.all_characters
        }
        self._validate_all_characters()

    def _load_characters(self) -> List[Dict[str, Any]]:
        """
        Loads the character profiles from the JSON file.

        Returns:
            A list of character dictionaries.

        Raises:
            FileNotFoundError: If the characters.json file is not found.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        try:
            with open(config.CHARACTERS_JSON_PATH, 'r', encoding='utf-8') as f:
                characters = json.load(f)
                self.logger.info(f"Successfully loaded {len(characters)} characters from {config.CHARACTERS_JSON_PATH}")
                return characters
        except FileNotFoundError:
            self.logger.error(f"CRITICAL: Character file not found at {config.CHARACTERS_JSON_PATH}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"CRITICAL: Failed to decode JSON from {config.CHARACTERS_JSON_PATH}")
            raise

    def _validate_all_characters(self):
        """
        Validates all loaded characters against rules in config.py.
        - Ensures required fields exist.
        - Ensures voices are in the available list.
        - Ensures gender is 'male' or 'female'.
        """
        required_keys = {"id", "name", "gender", "voice", "persona"}
        valid_genders = {"male", "female"}

        for char in self.all_characters:
            char_id = char.get('id', 'N/A')
            if not required_keys.issubset(char.keys()):
                raise ValueError(f"Character with id {char_id} is missing required keys. Found: {list(char.keys())}")

            if char['gender'] not in valid_genders:
                raise ValueError(
                    f"Character '{char['name']}' (id: {char_id}) has invalid gender: '{char['gender']}'. Must be 'male' or 'female'.")

            if char['voice'] not in config.AVAILABLE_VOICES:
                raise ValueError(
                    f"Character '{char['name']}' (id: {char_id}) has an unavailable voice: '{char['voice']}'. Check config.py.")

        self.logger.info("All character profiles validated successfully.")

    def select_show_participants(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Selects 2 hosts and 2 guests for a new show.
        Ensures one male and one female for both hosts and guests.

        Returns:
            A dictionary containing 'hosts' and 'guests' lists.
            Example: {'hosts': [char_dict_1, char_dict_2], 'guests': [char_dict_3, char_dict_4]}

        Raises:
            ValueError: If there are not enough characters to form a show.
        """
        males = [char for char in self.all_characters if char['gender'] == 'male']
        females = [char for char in self.all_characters if char['gender'] == 'female']

        # We need at least 2 males and 2 females to form a show as per the rules.
        if len(males) < config.NUM_HOSTS or len(females) < config.NUM_GUESTS:
            msg = (f"Insufficient characters to start a show. "
                   f"Need at least {config.NUM_HOSTS} males and {config.NUM_GUESTS} females. "
                   f"Found: {len(males)} males, {len(females)} females.")
            self.logger.error(msg)
            raise ValueError(msg)

        random.shuffle(males)
        random.shuffle(females)

        # For this project, hosts are always the first two characters in the JSON
        # and we select two random guests. This creates a consistent host pairing.
        # If dynamic hosts are desired, this logic can be changed.

        # Let's find the primary hosts by name for consistency
        try:
            host_male = next(c for c in males if c['name'] == 'Jack')
            host_female = next(c for c in females if c['name'] == 'Olivia')
        except StopIteration:
            self.logger.warning("Default hosts 'Jack' or 'Olivia' not found. Selecting random hosts.")
            host_male = males.pop(0)
            host_female = females.pop(0)

        # Guests are selected from the remaining pool
        available_male_guests = [c for c in males if c['id'] != host_male['id']]
        available_female_guests = [c for c in females if c['id'] != host_female['id']]

        if not available_male_guests or not available_female_guests:
            msg = "Insufficient unique guests to start a show after selecting hosts."
            self.logger.error(msg)
            raise ValueError(msg)

        guest_male = random.choice(available_male_guests)
        guest_female = random.choice(available_female_guests)

        selected_hosts = [host_male, host_female]
        selected_guests = [guest_male, guest_female]

        # Sort by gender for predictable ordering (e.g., male host is always first)
        selected_hosts.sort(key=lambda x: x['gender'], reverse=True)
        selected_guests.sort(key=lambda x: x['gender'], reverse=True)

        self.logger.info(f"Selected Hosts: {[h['name'] for h in selected_hosts]}")
        self.logger.info(f"Selected Guests: {[g['name'] for g in selected_guests]}")

        return {"hosts": selected_hosts, "guests": selected_guests}

    def get_character_by_id(self, character_id: int) -> Dict[str, Any]:
        """
        Retrieves a character's full data by their ID.

        Args:
            character_id: The ID of the character to find.

        Returns:
            The character's data dictionary.

        Raises:
            KeyError: If no character with the given ID is found.
        """
        try:
            return self.characters_by_id[character_id]
        except KeyError:
            self.logger.error(f"Could not find character with ID: {character_id}")
            raise