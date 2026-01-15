"""
character_manager.py
- ROTATIONAL HOSTS (Jack or Olivia).
- OPPOSITE GENDER GUESTS.
- 100+ DEEP EMOTIONAL PERSONAS.
"""

import json
import random
import logging
from typing import List, Dict, Any
import config

MALE_NAMES = ["James", "John", "Robert", "Michael", "David", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Walter", "Ethan", "Jeremy", "Harold", "Keith", "Christian", "Roger", "Noah", "Gerald", "Terry", "Sean", "Austin", "Carl", "Arthur", "Lawrence", "Dylan", "Jesse", "Jordan", "Bryan", "Billy", "Joe", "Bruce", "Gabriel", "Logan", "Albert", "Willie", "Alan", "Juan", "Wayne", "Roy", "Ralph", "Randy", "Eugene", "Vincent", "Russell", "Louis", "Philip", "Bobby", "Johnny", "Bradley"]

FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Laura", "Sharon", "Cynthia", "Kathleen", "Amy", "Shirley", "Angela", "Helen", "Anna", "Brenda", "Pamela", "Nicole", "Emma", "Samantha", "Katherine", "Christine", "Debra", "Rachel", "Catherine", "Carolyn", "Janet", "Ruth", "Maria", "Heather", "Diane", "Virginia", "Julie", "Joyce", "Victoria", "Olivia", "Kelly", "Christina", "Lauren", "Joan", "Evelyn", "Judith", "Megan", "Cheryl", "Andrea", "Hannah", "Martha", "Jacqueline", "Frances", "Gloria", "Ann", "Teresa", "Kathryn", "Sara", "Janice", "Jean", "Alice", "Madison", "Doris", "Abigail", "Julia", "Judy", "Grace", "Denise", "Amber", "Marilyn", "Beverly", "Danielle", "Theresa", "Sophia", "Marie", "Diana", "Brittany", "Natalie", "Isabella", "Charlotte", "Rose", "Kayla", "Alexis"]

# 100+ Deep, dramatic, viral-worthy relationship scenarios
RELATIONSHIP_STATUSES = [
    # CHEATING & BETRAYAL
    "Found her fiancé has a second family in another state.",
    "Caught him cheating with her sister at the rehearsal dinner.",
    "Found out he was married the whole 2 years they dated.",
    "She cheated on her husband with his boss to get a promotion.",
    "He slept with the nanny and now she's pregnant.",
    "Found scandalous texts on his phone from 10 different women.",
    "Her boyfriend left her for her best friend.",
    "He got another woman pregnant while they were 'on a break'.",
    "She caught him on Tinder while they were on their honeymoon.",
    "He admitted to having an affair with their marriage counselor.",

    # TOXIC EXES
    "Can't stop stalking her toxic ex on social media.",
    "Still sleeping with his ex-wife but hiding it from his fiancée.",
    "Her ex-boyfriend threatened to leak her private photos.",
    "He's still in love with his high school sweetheart who is married.",
    "She compares every new guy to her abusive ex.",
    "He broke up with her via text after 5 years.",
    "She refuses to return the engagement ring after dumping him.",
    "He showed up at her wedding to object.",
    "She keeps 'accidentally' running into her ex at the gym.",
    "He's paying his ex's rent and lying about it.",

    # FAMILY DRAMA
    "Her mother-in-law hates her and is trying to ruin the wedding.",
    "He chose his controlling mother over his wife.",
    "She's dating her step-brother (not blood related) and hiding it.",
    "His family cut him off for marrying a woman from a different religion.",
    "She's secretly dating her dad's business rival.",
    "He found out his 'son' isn't biologically his.",
    "Her sister stole her baby name and now they aren't speaking.",
    "He moved his parents into their house without asking.",
    "She's pregnant but doesn't know if it's her husband's or his brother's.",
    "His brother hit on her at Thanksgiving dinner.",

    # MONEY & CAREER
    "She makes 10x more than him and he's insecure about it.",
    "He spent their entire life savings on crypto without asking.",
    "She's dating a billionaire but has to sign a crazy NDA.",
    "He refuses to get a job and plays video games all day.",
    "She's a sugar baby falling in love with her sugar daddy.",
    "He stole money from her purse to gamble.",
    "She's secretly $100k in debt and hasn't told him.",
    "He wants a prenup and she's offended.",
    "She's only marrying him for his green card.",
    "He lost his job and lied about going to work for 6 months.",

    # SEXUAL & INTIMACY
    "Left her husband because the sex was boring.",
    "He wants an open relationship but she's jealous.",
    "She's secretly in love with a woman but married to a man.",
    "He has a fetish she can't accept.",
    "They haven't had sex in 3 years and don't know why.",
    "She found his secret OnlyFans account.",
    "He's addicted to porn and it's ruining their marriage.",
    "She wants kids but he got a secret vasectomy.",
    "He wants a threesome to 'save the marriage'.",
    "She's never had an orgasm with him and fakes it every time.",

    # AGE GAPS & TABOOS
    "Dating a man 20 years older and her friends judge her.",
    "He's dating a girl younger than his daughter.",
    "She fell in love with her professor.",
    "He's dating his boss and afraid of getting fired.",
    "She's dating a convicted felon who just got out.",
    "He's a priest falling in love with a parishioner.",
    "She's 40 and dating a 21-year-old college student.",
    "He's dating his best friend's mom.",
    "She's dating her ex's dad.",
    "He's in a relationship with two women who know about each other.",

    # MODERN DATING HELL
    "Got ghosted after saying 'I love you'.",
    "Met a guy online who turned out to be a catfish.",
    "She's addicted to dating apps and can't commit.",
    "He brought his mom on their first date.",
    "She went on a date just for the free expensive dinner.",
    "He split the bill on a $10 coffee date.",
    "She found out he has a secret Instagram for his dog.",
    "He wears a toupee and she accidentally pulled it off.",
    "She's dating a 'digital nomad' who lives in a van.",
    "He refuses to post her on social media.",

    # EMOTIONAL BAGGAGE
    "Still grieving her late husband and feels guilty dating.",
    "He's afraid of commitment because his parents divorced.",
    "She pushes people away as soon as they get close.",
    "He's a narcissist who gaslights her constantly.",
    "She has major trust issues after being cheated on.",
    "He's emotionally unavailable and cold.",
    "She's codependent and can't do anything alone.",
    "He's overly jealous and checks her phone.",
    "She's dating him out of pity.",
    "He's still traumatized by his ex's death.",

    # WILD CARD / VIRAL
    "She thinks her boyfriend is a spy.",
    "He believes aliens abducted him and it ruined his marriage.",
    "She's dating a man who thinks he's a vampire.",
    "He joined a cult and wants her to join too.",
    "She's in love with a prisoner she's never met.",
    "He won the lottery and hid it from his wife.",
    "She faked a pregnancy to keep him.",
    "He faked his own death to escape his wife.",
    "She's dating a ghost hunter.",
    "He thinks the earth is flat and she can't deal with it."
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
