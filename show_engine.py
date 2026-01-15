"""
show_engine.py
- FORMAT: Adaptive 1-on-1 Conversation (Changes based on each story).
- TONE: Natural, Reactive, Unique to each guest's experience.
- LENGTH: 250-300+ Lines (8-10 minutes).
- APPROACH: Story-first, not template-first.
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

        # --- GENDER LOGIC FIX ---
        # If guest is male, partner is female. If guest is female, partner is male.
        partner_gender = "female" if guest['gender'] == 'male' else 'male'
        partner_pronouns = "she/her" if partner_gender == 'female' else "he/him"
        partner_label = "woman" if partner_gender == 'female' else "man"
        
        prompt = f"""
You are writing a raw, unrehearsed conversation for "The Ex-Files."

**WHO'S IN THE ROOM:**
{host['name']} ({host['gender']}) - Speaker ID: {host['id']} - The host. Empathetic but curious. Knows when to dig deeper.
{guest['name']} ({guest['gender']}) - Speaker ID: {guest['id']} - Today's story: "{guest['persona']}"

**CRITICAL PRONOUN & GENDER RULE:**
1. The person {guest['name']} is talking about is a {partner_gender}.
2. DO NOT use "they/them" pronouns to refer to the partner. 
3. ALWAYS use "{partner_pronouns}" and "{partner_label}" when referring to the person the guest is talking about.
4. If the guest is male, he is talking about a woman. If the guest is female, she is talking about a man.

**YOUR MISSION:**
Create a conversation that is COMPLETELY UNIQUE to {guest['name']}'s specific situation. 

✅ **ASK QUESTIONS THAT ARE SPECIFIC TO THIS EXACT STORY:**
Instead of "How did they make you feel?", ask "Wait, so SHE just left the dinner table and never came back?" or "Did HE actually try to tell you the ring was a prop?"

**THE FORMULA:**
1. Read {guest['name']}'s story: "{guest['persona']}"
2. Imagine the SPECIFIC details only THIS story would have.
3. Use the correct pronouns ({partner_pronouns}) throughout.
4. Follow the thread of THEIR story, not a template.

---

**CONVERSATION STRUCTURE (400-800+ LINES):**

**ACT 1: SETTLING IN (30-50 lines)**
- Natural greeting, notice their energy. Small talk that reveals personality. No "welcome to the show" - start human.

**ACT 2: THE SETUP (50-90 lines)**
- How did this situation even START? Specific details about how they met this {partner_gender}. Early warning signs.

**ACT 3: THE STORY UNFOLDS (90-150 lines)**
This is the MEAT. Dig into the specifics of THEIR unique situation. Ask about the exact moment of discovery. React authentically: "Wait, WHAT?" or "I did not see that coming."

**ACT 4: THE AFTERMATH (80-120 lines)**
What happened next? The confrontation scene. What {guest['name']} said to {partner_pronouns}. Who took whose side?

**ACT 5: WHERE THEY ARE NOW (70-100 lines)**
Current reality. No neat bows. How has this changed them? Regrets? Lessons?

**ACT 6: THE CLOSE (40-60 lines)**
- Final thoughts from {guest['name']}. {host['name']} validates them. Turn to audience with authentic CTA.

---

**CRITICAL WRITING RULES:**

✅ **MAKE IT SPECIFIC TO THE STORY:**
Every question should be something you could ONLY ask about THIS particular situation.

✅ **PRONOUN CONSISTENCY:**
If {guest['name']} is male, the partner is SHE. If {guest['name']} is female, the partner is HE. No "they" allowed.

✅ **LET THE CONVERSATION BREATHE:**
- Short lines (1-3 sentences each). Natural interruptions. Pauses and reactions.

✅ **REACT LIKE A REAL PERSON:**
{host['name']} is not a therapist. They're a human. "That's wild," "I would've lost it," or "[long pause]".

---

**STRATEGIC CLIFFHANGERS:**
Place natural "OMG WHAT?!" moments around:
- Line 75-85: First major reveal.
- Line 150-165: The confrontation or worst moment.
- Line 225-240: Current complications.

**OUTPUT FORMAT - RETURN ONLY VALID JSON:**

You must return your response as a JSON object with this exact structure:

{{
  "dialogue": [
    {{"speaker_id": {host['id']}, "text": "[Opening line specific to story]"}},
    {{"speaker_id": {guest['id']}, "text": "[Response]"}}
  ]
}}

**ABSOLUTE REQUIREMENTS:**
1. ONLY use speaker_id: {host['id']} for {host['name']}, {guest['id']} for {guest['name']}
2. **MINIMUM 250 LINES OF DIALOGUE**
3. Use {partner_pronouns} exclusively for the partner.
4. No markdown formatting. No explanations. Just valid JSON.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a master dialogue writer. You strictly use {partner_pronouns} for the partner in this script. You generate 250+ line conversations in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                model=config.GROQ_LLM_MODEL,
                temperature=0.95,
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
            name_map = {
                host['name'].lower(): host['id'],
                guest['name'].lower(): guest['id'],
                'host': host['id'],
                'guest': guest['id']
            }
            
            for i, line in enumerate(script):
                speaker = line.get('speaker_id')
                if isinstance(speaker, str):
                    speaker_lower = speaker.lower().strip()
                    if speaker_lower in name_map:
                        line['speaker_id'] = name_map[speaker_lower]
                    else:
                        line['speaker_id'] = guest['id']
                elif isinstance(speaker, int):
                    if speaker not in [host['id'], guest['id']]:
                        line['speaker_id'] = guest['id']

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            return script

        except Exception as e:
            self.logger.critical(f"Script generation error: {e}")
            raise
