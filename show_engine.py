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
        
        prompt = f"""
You are writing a raw, unrehearsed conversation for "The Ex-Files."

**WHO'S IN THE ROOM:**
{host['name']} ({host['gender']}) - Speaker ID: {host['id']} - The host. Empathetic but curious. Knows when to dig deeper.
{guest['name']} ({guest['gender']}) - Speaker ID: {guest['id']} - Today's story: "{guest['persona']}"

**YOUR MISSION:**
Create a conversation that is COMPLETELY UNIQUE to {guest['name']}'s specific situation. 

❌ **DO NOT USE GENERIC QUESTIONS LIKE:**
- "How did that make you feel?"
- "Tell me about your relationship."
- "When did things change?"
- "What would you say to them now?"

✅ **INSTEAD, ASK QUESTIONS THAT ARE SPECIFIC TO THIS EXACT STORY:**

**FOR EXAMPLE:**

If the story is "Found out he was married the whole 2 years they dated":
- "Wait, so you met his 'roommate' who was actually his WIFE?"
- "Did you ever wonder why you never went to his place?"
- "When you found the wedding ring, what went through your head?"
- "His wife didn't know about you either, right? Did you two ever talk?"

If the story is "She caught him on Tinder while they were on their honeymoon":
- "Honeymoon. HONEYMOON. Where were you when you saw his profile?"
- "Did he use a photo from the wedding?"
- "What did his bio say? Was he pretending to be single?"
- "Did you swipe right just to match with him and call him out?"

If the story is "He's still in love with his high school sweetheart who is married":
- "Does your current partner know you're still thinking about her?"
- "Do you follow her on social media? See her kids, her life?"
- "Have you ever reached out? Or thought about it?"
- "What would you do if she got divorced tomorrow?"

**THE FORMULA:**
1. Read {guest['name']}'s story: "{guest['persona']}"
2. Imagine the SPECIFIC details only THIS story would have
3. Ask about THOSE details, not generic relationship stuff
4. React to what they say like a real person would
5. Follow the thread of THEIR story, not a template

---

**CONVERSATION STRUCTURE (250-300+ LINES):**

**ACT 1: SETTLING IN (30-40 lines)**
- Natural greeting, notice their energy
- Small talk that reveals personality
- Ease into the topic naturally
- Let them decide when to start the real story
- No "welcome to the show" - start human

**ACT 2: THE SETUP (50-70 lines)**
- How did this situation even START?
- Specific details about how they met this person
- What was their life like before this happened?
- Early warning signs they might have missed
- Build the world so we understand the context
- Let {guest['name']} paint the picture their way

**ACT 3: THE STORY UNFOLDS (80-100 lines)**
This is the MEAT. Dig into the specifics of THEIR unique situation.

Ask questions ONLY this story would have:
- About the specific betrayal method
- About the other people involved (if any)
- About the exact moment of discovery
- About details that make THIS story different from all others
- About what happened in the hours/days after

React authentically:
- "Wait, WHAT?" 
- "I did not see that coming."
- "Hold on, go back - your SISTER?!"
- "That's insane."
- Let the conversation flow based on what they reveal

**ACT 4: THE AFTERMATH (60-80 lines)**
What happened next? This varies HUGELY by story type.

For betrayal stories:
- The confrontation scene (blow by blow)
- What the other person said
- Who took whose side
- Are they still together/married/in contact?

For unrequited love stories:
- How do they manage these feelings?
- Does the other person know?
- What about current relationships?

For family drama stories:
- How did holidays go after?
- Who got cut off?
- Any reconciliation attempts?

For modern dating disasters:
- Did they ever see them again?
- What did their friends say?
- Are they still on the apps?

**ACT 5: WHERE THEY ARE NOW (40-60 lines)**
Current reality. No neat bows.

- What's their life like today?
- How has this changed them?
- Regrets? Lessons? Growth?
- Would they do anything differently?
- What do they want people to know?

**ACT 6: THE CLOSE (20-30 lines)**
- Final thoughts from {guest['name']}
- {host['name']} validates their experience
- Turn to audience with authentic CTA
- Make it feel complete but not preachy

---

**CRITICAL WRITING RULES:**

✅ **MAKE IT SPECIFIC TO THE STORY:**
Every question should be something you could ONLY ask about THIS particular situation.

Example - BAD (generic):
- Host: "So when did you realize something was wrong?"
- Guest: "I just had a feeling."

Example - GOOD (specific to "He spent their entire life savings on crypto"):
- Host: "Wait, so you went to buy groceries and your card got declined?"
- Guest: "Yeah. And I was like, that's weird, we had like $50,000 last month."
- Host: "When did you check the account?"
- Guest: "That night. It was at $47. Forty. Seven. Dollars."
- Host: "Jesus. What did he say when you confronted him?"
- Guest: "That Bitcoin was about to moon and we'd be millionaires."
- Host: "Is he a millionaire now?"
- Guest: "He's living in his mom's basement."

✅ **LET THE CONVERSATION BREATHE:**
- Short lines (1-3 sentences each)
- Natural interruptions
- Pauses and reactions
- Backtracking when they remember something
- "Wait, I should explain first..."
- "Actually, that's not even the worst part."

✅ **REACT LIKE A REAL PERSON:**
{host['name']} is not a therapist. They're a human having a conversation.
- "That's wild."
- "I would've lost it."
- "You're stronger than me."
- "I can't believe they said that."
- Sometimes just: "Wow." or "[long pause]"

✅ **INCLUDE CONTRADICTIONS:**
Real people have messy feelings:
- "I hate them. But I miss them."
- "It was the worst thing that ever happened to me. But I'm weirdly grateful now?"
- "I know I should move on. But what if they come back?"

✅ **USE THE 5 W's FOR SPECIFICITY:**
- WHO exactly was involved? Names, relationships, ages
- WHAT exactly happened? Actions, words, locations
- WHEN exactly? Time of day, season, how long ago
- WHERE exactly? Their house, a car, a restaurant, social media
- WHY did this happen? (Or why do they think it happened?)

---

**STRATEGIC CLIFFHANGERS (for multi-part engagement):**

Place natural "OMG WHAT?!" moments around:

**Line 75-85 (End of Part 1):**
The first major reveal or twist in the story.
- "And that's when I found out they had a whole other family."
- "Turns out, my best friend had known the whole time."
- "I opened the door and saw them. Together."

**Line 150-165 (End of Part 2):**
The confrontation or worst moment.
- "So I told them exactly what I found. And they LAUGHED."
- "I asked if they loved me. They said... nothing."
- "That's when I realized they'd been lying about everything."

**Line 225-240 (End of Part 3):**
Current complications or unresolved feelings.
- "And I saw them last week. At my workplace. With their new partner."
- "Sometimes I think about reaching out. Is that crazy?"
- "The worst part? I still check their Instagram every single day."

**Line 280-300 (End - Resolution):**
Final thoughts, growth, message to audience.

---

**TONE VARIATIONS BY STORY TYPE:**

**Betrayal/Cheating stories:** Angry → Hurt → Processing → Growth
**Unrequited love stories:** Longing → Frustration → Acceptance → Hope
**Family drama stories:** Confused → Angry → Sad → Boundaries
**Modern dating disasters:** Shocked → Amused → Frustrated → Cautious
**Toxic relationship stories:** Defensive → Realization → Escape → Healing

Match the emotional arc to the story type.

---

**OUTPUT FORMAT - RETURN ONLY VALID JSON:**

You must return your response as a JSON object with this exact structure:

{{
  "dialogue": [
    {{"speaker_id": {host['id']}, "text": "[Opening line specific to this story]"}},
    {{"speaker_id": {guest['id']}, "text": "[Response]"}},
    {{"speaker_id": {host['id']}, "text": "[Follow-up question based on their answer]"}}
  ]
}}

No markdown formatting. No explanations. Just valid JSON.

**ABSOLUTE REQUIREMENTS:**
1. ONLY use speaker_id: {host['id']} for {host['name']}, {guest['id']} for {guest['name']}
2. **MINIMUM 250 LINES OF DIALOGUE - THIS IS NON-NEGOTIABLE**
3. Every question must be SPECIFIC to "{guest['persona']}"
4. No generic therapy speak
5. Natural, reactive conversation flow
6. Strategic cliffhangers for multi-part engagement
7. Emotional authenticity over polish

**LINE COUNT VALIDATION:**
Before you finish, count your dialogue array. If it has fewer than 250 entries, ADD MORE LINES.
Do NOT submit a script with fewer than 250 lines. The conversation should be 8-10 minutes long.
If you're at 100 lines and wrapping up, YOU'RE DOING IT WRONG - keep going!

Remember: 250+ lines MINIMUM. Not 50. Not 100. Not even 200. At LEAST 250 lines of back-and-forth dialogue.

---

**FINAL CHECK BEFORE YOU WRITE:**

Read the story again: "{guest['persona']}"

Ask yourself:
- What are the UNIQUE details this story would have that others wouldn't?
- What would I be dying to know if my friend told me this story?
- What's the most shocking/surprising/interesting part of THIS specific situation?
- How would a real conversation about THIS unfold?

Then write THAT conversation. Not a template. Not a format. The actual, messy, specific, can't-look-away conversation about {guest['name']}'s unique experience.

Make it so specific that if someone heard this without context, they'd know EXACTLY which story it is.

GO.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a master dialogue writer. You create natural, engaging 250+ line conversations in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                model=config.GROQ_LLM_MODEL,
                temperature=0.95,  # Even higher for more unique, creative responses
                max_tokens=8000,
                response_format={"type": "json_object"}, 
            )
            
            content = chat_completion.choices[0].message.content
            data = json.loads(content)
            
            # Extract script from nested JSON
            if isinstance(data, dict):
                key = next(iter(data))
                script = data[key]
            else:
                script = data

            # Enhanced ID Fixer with detailed logging
            name_map = {
                host['name'].lower(): host['id'],
                guest['name'].lower(): guest['id'],
                'host': host['id'],
                'guest': guest['id']
            }
            
            for i, line in enumerate(script):
                speaker = line.get('speaker_id')
                original_speaker = speaker
                
                # Convert string names to integer IDs
                if isinstance(speaker, str):
                    speaker_lower = speaker.lower().strip()
                    
                    # Try direct name match
                    if speaker_lower in name_map:
                        line['speaker_id'] = name_map[speaker_lower]
                    else:
                        # Unknown speaker - log warning and default to guest
                        self.logger.warning(f"Line {i}: Unknown speaker '{speaker}', defaulting to guest ({guest['id']})")
                        line['speaker_id'] = guest['id']
                
                # Validate integer IDs
                elif isinstance(speaker, int):
                    if speaker not in [host['id'], guest['id']]:
                        self.logger.warning(f"Line {i}: Invalid speaker_id {speaker}, defaulting to guest ({guest['id']})")
                        line['speaker_id'] = guest['id']
                
                # Log conversions for debugging
                if original_speaker != line['speaker_id']:
                    self.logger.debug(f"Line {i}: Converted speaker '{original_speaker}' -> {line['speaker_id']}")

            self.logger.info(f"[{show_id}] Script generated. Length: {len(script)} lines.")
            
            # Validation check
            if len(script) < 250:
                self.logger.warning(f"Script only has {len(script)} lines (target: 250+). Audio may be shorter than 8 minutes.")
            else:
                estimated_minutes = (len(script) * 2) / 60  # Rough estimate: 2 seconds per line
                self.logger.info(f"Estimated audio length: ~{estimated_minutes:.1f} minutes")
            
            return script

        except json.JSONDecodeError as e:
            self.logger.critical(f"JSON parsing error: {e}")
            self.logger.critical(f"Raw content: {content[:500]}")
            raise
        except Exception as e:
            self.logger.critical(f"Script generation error: {e}")
            raise
