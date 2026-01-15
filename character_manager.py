"""
character_manager.py
- ROTATIONAL HOSTS (Jack or Olivia).
- OPPOSITE GENDER GUESTS.
- DEEP EMOTIONAL PERSONAS.
"""

import json
import random
import logging
from typing import List, Dict, Any
import config

MALE_NAMES = ["James", "John", "Robert", "Michael", "David", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Walter", "Ethan", "Jeremy", "Harold", "Keith", "Christian", "Roger", "Noah", "Gerald", "Terry", "Sean", "Austin", "Carl", "Arthur", "Lawrence", "Dylan", "Jesse", "Jordan", "Bryan", "Billy", "Joe", "Bruce", "Gabriel", "Logan", "Albert", "Willie", "Alan", "Juan", "Wayne", "Roy", "Ralph", "Randy", "Eugene", "Vincent", "Russell", "Louis", "Philip", "Bobby", "Johnny", "Bradley"]

FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Sharon", "Cynthia", "Kathleen", "Amy", "Shirley", "Angela", "Helen", "Anna", "Brenda", "Pamela", "Nicole", "Emma", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Catherine", "Carolyn", "Janet", "Ruth", "Maria", "Heather", "Diane", "Virginia", "Julie", "Joyce", "Victoria", "Olivia", "Kelly", "Christina", "Lauren", "Joan", "Evelyn", "Judith", "Megan", "Cheryl", "Andrea", "Hannah", "Martha", "Jacqueline", "Frances", "Gloria", "Ann", "Teresa", "Kathryn", "Sara", "Janice", "Jean", "Alice", "Madison", "Doris", "Abigail", "Julia", "Judy", "Grace", "Denise", "Amber", "Marilyn", "Beverly", "Danielle", "Theresa", "Sophia", "Marie", "Diana", "Brittany", "Natalie", "Isabella", "Charlotte", "Rose", "Kayla", "Alexis"]

# Deep, dramatic relationship scenarios
RELATIONSHIP_STATUSES = [
    "Just found out her fiancé has a second family.",
    "Secretly in love with his brother's wife.",
    "Left her husband because the sex was boring.",
    "Can't stop texting his toxic ex-girlfriend.",
    "Dating a man 20 years older and her parents hate it.",
    "Cheated on his wife at his bachelor party.",
    "Still sleeping with her ex-husband.",
    "Thinks her boyfriend is gay but he won't admit it.",
    "In a polyamorous relationship that is falling apart.",
    "Obsessed with stalking his ex on Instagram."
]

class CharacterManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.static_hosts = self._load_static_characters()
        self.characters_by_id = {char['id']: char for char in self.static_hosts}

    def _load_static_characters(self) -> List[Dict[str, Any]]:
        # Jack and Olivia are the only permanent residents
        return [
            {"id": 1, "name": "Jack", "gender": "male", "voice": "host_male"},
            {"id": 2, "name": "Olivia", "gender": "female", "voice": "host_female"}
        ]

    def select_show_participants(self) -> Dict[str, List[Dict[str, Any]]]:
        # 1. Randomly pick ONE host
        host = random.choice(self.static_hosts)
        
        # 2. Generate OPPOSITE gender guest
        if host['gender'] == 'male':
            guest_name = random.choice(FEMALE_NAMES)
            guest_gender = 'female'
        else:
            guest_name = random.choice(MALE_NAMES)
            guest_gender = 'male'

        guest = {
            "id": 100,
            "name": guest_name,
            "gender": guest_gender,
            "voice": "guest_voice", # The engine will map this based on gender
            "persona": random.choice(RELATIONSHIP_STATUSES)
        }

        # Update lookup
        self.characters_by_id[100] = guest

        self.logger.info(f"Show Cast: Host={host['name']} ({host['gender']}) vs Guest={guest['name']} ({guest['gender']})")
        self.logger.info(f"Topic: {guest['persona']}")

        return {
            "hosts": [host],
            "guests": [guest]
        }

    def get_character_by_id(self, character_id: int) -> Dict[str, Any]:
        return self.characters_by_id[character_id]
