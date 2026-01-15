"""
character_manager.py

Manages characters for the radio show.
- HOSTS: Static (Jack & Olivia). Persisted in characters.json.
- GUESTS: DYNAMIC. Generated fresh for every single show.
- ENSURES CONSISTENT VOICE MAPPING.
"""

import json
import random
import logging
from typing import List, Dict, Any

import config

# Lists for random generation
MALE_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Christopher", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth",
    "Joshua", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
    "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry"
]

FEMALE_NAMES = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Nancy", "Lisa", "Margaret", "Betty", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna",
    "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Sharon", "Cynthia",
    "Kathleen", "Amy", "Shirley", "Angela", "Helen", "Anna", "Brenda", "Pamela", "Nicole", "Emma",
    "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Catherine", "Carolyn", "Janet", "Ruth", "Maria"
]

PERSONAS = [
    "A nervous accountant.", "A loud fitness trainer.", "A cynical barista.", "A hopelessly romantic librarian.",
    "A tech bro obsessed with crypto.", "A free-spirited artist.", "A strict school teacher.", "A tired nurse.",
    "A chaotic influencer.", "A shy gamer.", "A pretentious food critic.", "A laid-back surfer.",
    "A neurotic dog walker.", "A wealthy real estate agent.", "A struggling musician."
]

class CharacterManager:
    """Handles static hosts and dynamic guests."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.all_characters = self._load_static_characters()
        
        # Initialize lookup table with static hosts
        self.characters_by_id = {char['id']: char for char in self.all_characters}

    def _load_static_characters(self) -> List[Dict[str, Any]]:
        """Loads only the fixed hosts from JSON."""
        try:
            with open(config.CHARACTERS_JSON_PATH, 'r', encoding='utf-8') as f:
                chars = json.load(f)
                # We only want Jack (1) and Olivia (2) to be permanent
                hosts = [c for c in chars if c['id'] in [1, 2]]
                if len(hosts) < 2:
                    raise ValueError("characters.json must contain ID 1 (Jack) and ID 2 (Olivia)")
                return hosts
        except Exception as e:
            self.logger.error(f"Failed to load characters: {e}")
            raise

    def select_show_participants(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Selects the 2 static hosts and GENERATES 2 new guests.
        """
        # 1. Get Static Hosts
        host_male = self.characters_by_id[1]  # Jack
        host_female = self.characters_by_id[2] # Olivia

        # 2. Generate New Guests
        # We assign them temporary IDs 100 (Male) and 101 (Female)
        
        guest_male_name = random.choice(MALE_NAMES)
        guest_female_name = random.choice(FEMALE_NAMES)
        
        # Ensure guests don't have same name as hosts
        while guest_male_name == host_male['name']: guest_male_name = random.choice(MALE_NAMES)
        while guest_female_name == host_female['name']: guest_female_name = random.choice(FEMALE_NAMES)

        guest_male = {
            "id": 100, # Fixed ID for "The Male Guest" slot
            "name": guest_male_name,
            "gender": "male",
            "voice": "vits_male_02", # Maps to p237 (Guest Male Voice)
            "persona": random.choice(PERSONAS)
        }

        guest_female = {
            "id": 101, # Fixed ID for "The Female Guest" slot
            "name": guest_female_name,
            "gender": "female",
            "voice": "vits_female_02", # Maps to p236 (Guest Female Voice)
            "persona": random.choice(PERSONAS)
        }

        # 3. Register Dynamic Guests into Lookup Table
        # This ensures get_character_by_id(100) works during audio generation
        self.characters_by_id[100] = guest_male
        self.characters_by_id[101] = guest_female

        self.logger.info(f"Show Cast: Hosts={host_male['name']}&{host_female['name']} | Guests={guest_male['name']}&{guest_female['name']}")

        return {
            "hosts": [host_male, host_female],
            "guests": [guest_male, guest_female]
        }

    def get_character_by_id(self, character_id: int) -> Dict[str, Any]:
        """Retrieves character data, working for both static and dynamic IDs."""
        try:
            return self.characters_by_id[character_id]
        except KeyError:
            self.logger.error(f"Could not find character with ID: {character_id}")
            raise
