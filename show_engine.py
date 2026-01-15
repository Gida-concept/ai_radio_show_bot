"""
show_engine.py
- FORMAT: 1-on-1 Intimate Conversation (NOT interview-style).
- TONE: Natural, Progressive, Human, Real.
- LENGTH: EXTENDED (130+ Lines).
- FLOW: Organic progression from small talk to deep vulnerability.
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
You are writing a deeply HUMAN conversation for "The Ex-Files" - a show where two people just... talk. Really talk.

**THE PEOPLE IN THIS ROOM:**
{host['name']} ({host['gender']}) - Speaker ID: {host['id']} - The host. Warm, empathetic, knows when to push and when to just listen.
{guest['name']} ({guest['gender']}) - Speaker ID: {guest['id']} - Today's guest. Dealing with: "{guest['persona']}"

**CRITICAL: This is NOT a formal interview. This is two humans connecting.**

Think of it like this: {guest['name']} agreed to come on the show because they need to talk. {host['name']} creates a safe space where the truth can come out naturally, not forced.

**THE CONVERSATION SHOULD FLOW LIKE THIS (130-150 lines):**

**PHASE 1: THE WARM-UP (15-20 lines)**
They're settling in. {guest['name']} is nervous, maybe second-guessing this whole thing.

- {host['name']} notices body language: "You okay? You seem... tense."
- Small talk that reveals character: "Did you have trouble finding the place?" / "Want some water? Coffee?"
- {guest['name']} deflects at first: "I'm fine, yeah, let's just... let's do this."
- {host['name']} doesn't push yet: "No rush. We've got time. Just breathe."
- Maybe a small joke to break tension, a shared laugh
- Gradually easing into: "So... you ready to talk about it?"
- {guest['name']}: "I don't know. Maybe. I think I need to."

**PHASE 2: THE OPENING UP (25-30 lines)**
{guest['name']} starts sharing, but still guarded. Testing the waters.

- Starts with the "safe" parts: "We were together for [X] years."
- Talks about how they met: specific details, real memories
- {host['name']} relates: "I remember that feeling. When everything just... clicks."
- {guest['name']} gets a little nostalgic: describes a perfect moment
- {host['name']} asks gentle questions: "What did you love most about them?"
- {guest['name']} opens up more: real traits, quirks, inside jokes
- But then catches themselves: "I don't know why I'm telling you this."
- {host['name']}: "Because it mattered. It's okay that it mattered."
- Small pause. {guest['name']} nods, continues.

**PHASE 3: THE SHIFT (20-25 lines)**
The mood changes. Something isn't being said.

- {host['name']} notices the shift: "You just... your whole face changed. What are you thinking about?"
- {guest['name']} deflects: "Nothing. I mean... it's stupid."
- {host['name']}: "It's not stupid if it's bothering you."
- {guest['name']} admits something small: a red flag they ignored
- {host['name']} doesn't judge: "Did you know then? Or did you convince yourself...?"
- {guest['name']}: "I convinced myself. For months."
- They go back and forth, {guest['name']} revealing more with each exchange
- {host['name']} shares their own experience briefly (relatable, builds trust)
- {guest['name']} realizes they're not alone: "Wait, you too?"
- Connection deepens. The walls are coming down.

**PHASE 4: THE HEART OF IT (40-50 lines)**
This is where the real story comes out. Not rushed. Natural progression.

- {guest['name']} starts to tell what happened, but it's messy
- They backtrack: "Wait, I should explain first—"
- {host['name']}: "Take your time. I'm not going anywhere."
- {guest['name']} describes the moment things changed: 
  * A specific day, a specific feeling
  * Something they saw, heard, or realized
  * The exact moment their gut told them something was wrong
  
- {host['name']} asks clarifying questions (not interrogating, just understanding):
  * "What did you do when you realized?"
  * "Did you confront them right away?"
  * "What did they say?"
  
- {guest['name']}'s emotions start showing:
  * Voice gets shaky
  * Pauses get longer
  * Maybe anger breaks through: "I was so STUPID."
  * {host['name']}: "You weren't stupid. You were in love."
  
- The full story unfolds with specific details:
  * Real conversations they had
  * Exact words that were said
  * Physical sensations: "My hands were shaking" / "I couldn't breathe"
  * What they saw, what they heard, what broke them
  
- {host['name']} validates without fixing:
  * "That's so heavy to carry."
  * "How did you even... how did you get through that?"
  * Sometimes just: "Yeah." or "[long pause]" or "Damn."
  
- {guest['name']} reveals layers:
  * What they told their friends vs. what really happened
  * What they still haven't told anyone
  * The part that still keeps them up at night

**PHASE 5: THE COMPLEXITY (25-30 lines)**
Feelings aren't simple. Explore the gray areas.

- {host['name']}: "Do you ever... miss them?"
- {guest['name']} struggles to answer honestly
- Admits contradictions: "I hate them. But I also... I don't know."
- {host['name']}: "You can hate what they did and still miss who they were."
- {guest['name']}: "Is that normal? Am I crazy?"
- They talk about the aftermath:
  * Seeing them with someone new
  * Mutual friends taking sides
  * How holidays feel now
  * Dating again (or not being able to)
  
- {host['name']} asks the hard question: "If they walked in right now and apologized, would you take them back?"
- {guest['name']}'s answer is complicated, human, real
- They discuss what moving on actually means
- {guest['name']}: "Sometimes I check their Instagram. Is that pathetic?"
- {host['name']}: "It's human. We all do things that don't make sense when we're healing."

**PHASE 6: THE TURNING POINT (15-20 lines)**
Finding meaning, growth, or at least acceptance.

- {host['name']}: "What's different now? Like, how are YOU different?"
- {guest['name']} reflects on what they learned
- Maybe there's humor now: a dark joke about the situation
- Both laugh—genuine, cathartic laughter
- {guest['name']}: "I never thought I'd be able to laugh about this."
- {host['name']}: "That's growth right there."
- They talk about hope:
  * What {guest['name']} wants now
  * What scares them about trying again
  * Small wins: "I stopped checking their page last week"
  
- {guest['name']}: "Thank you for letting me just... talk."
- {host['name']}: "Thank you for trusting me with this."

**PHASE 7: THE OUTRO (10-12 lines)**
Wrapping up naturally, then turning to the audience.

- {host['name']} to {guest['name']}: "You're gonna be okay. You know that, right?"
- {guest['name']}: "I'm starting to believe it."
- {host['name']}: "Good. Because you will be."
- [Beat]
- {host['name']} to audience:
  * "If you made it this far, thank you for listening to {guest['name']}'s story."
  * "If this resonated with you—if you've been there—leave a comment. Share your story. We're all figuring this out together."
  * "And if you know someone who needs to hear this, send it to them. Sometimes we need to know we're not alone."
  * "Hit follow for more conversations like this. Real people, real stories."
  * "Thanks for being here. Take care of yourselves."

---

**WRITING RULES FOR NATURAL FLOW:**

✅ **DO THIS:**
- Let conversations breathe with pauses: "[pause]" / "[long silence]"
- Interrupt naturally: "I just—" "Wait, you—" "But—"
- Circle back to earlier points: "Remember you said...?"
- Use filler words: "like," "you know," "I mean," "kind of"
- Show emotional progression: starts guarded → opens up → breaks down → finds strength
- Include small human moments: 
  * "You need a tissue?"
  * "[laughs nervously]"
  * "Sorry, I'm rambling."
  * "Does that make sense?"
- React authentically:
  * {host['name']}: "Wow." / "I didn't see that coming." / "Oh man."
  * {guest['name']}: "Right?!" / "I know, I know." / "Don't even get me started."

❌ **DON'T DO THIS:**
- Generic therapist phrases: "How did that make you feel?" ❌
- Jumping topics randomly ❌
- Formal interview questions: "Let's move on to..." ❌
- Perfectly articulated thoughts (people stumble!) ❌
- Resolving everything neatly (life is messy) ❌
- Making it sound scripted ❌

---

**SPECIFIC STORYTELLING TECHNIQUES:**

1. **THE BREADCRUMB METHOD:**
   - Don't dump the whole story at once
   - Drop hints: "That wasn't even the worst part."
   - Build curiosity: "Wait till you hear what happened next."
   - Let {host['name']} pick up on threads: "Wait, go back—you said your sister?"

2. **SENSORY DETAILS:**
   - "I remember the smell of her perfume in the car."
   - "His hands were cold when he finally told me."
   - "I can still hear the sound of the door closing."

3. **SPECIFIC MOMENTS OVER SUMMARIES:**
   Bad: "We fought a lot." ❌
   Good: "One night, he threw his keys at the wall so hard they left a dent. We both just stared at it." ✅

4. **CONTRADICTIONS = HUMANITY:**
   - "I hate him." [pause] "I miss him." [pause] "Both things are true."
   - "She ruined my life." [pause] "But I hope she's happy." [pause] "Is that weird?"

---

**OUTPUT FORMAT:**

Return ONLY valid JSON:

{{
  "dialogue": [
    {{"speaker_id": {host['id']}, "text": "Hey. You okay? You look like you're about to bolt."}},
    {{"speaker_id": {guest['id']}, "text": "I'm... yeah, I'm fine. Just nervous, I guess. Is that weird?"}},
    {{"speaker_id": {host['id']}, "text": "Not at all. Most people are. You want some water before we start?"}}
  ]
}}

**ABSOLUTE REQUIREMENTS:**
1. ONLY use speaker_id: {host['id']} (for {host['name']}) and {guest['id']} (for {guest['name']})
2. 130-150 lines minimum
3. Natural progression—no jumps
4. Specific details, not generic statements
5. Emotional honesty—messy, real, human
6. Build trust gradually—don't rush to the trauma
7. One host ({host['name']}), one guest ({guest['name']})—that's it

Write a conversation that feels like eavesdropping on two people who genuinely care about each other's stories. Make it REAL.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=config.GROQ_LLM_MODEL,
                temperature=0.9,  # Higher temp for more natural, less formulaic responses
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
            if len(script) < 130:
                self.logger.warning(f"Script only has {len(script)} lines (target: 130+)")
            
            return script

        except json.JSONDecodeError as e:
            self.logger.critical(f"JSON parsing error: {e}")
            self.logger.critical(f"Raw content: {content[:500]}")
            raise
        except Exception as e:
            self.logger.critical(f"Script generation error: {e}")
            raise
