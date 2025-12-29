#!/usr/bin/env python3
"""
N.I.K — Fast, chill, human-like chatbot
Enhanced for ultra-natural conversations
"""

import os
import time
import json
import random
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# =====================
# CONFIG
# =====================
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
MEMORY_FILE = "nik_memory.json"

MAX_NEW_TOKENS = 400
TEMPERATURE = 0.8  # default, modes may override
TOP_P = 0.9
REPETITION_PENALTY = 1.15

# =====================
# MEMORY
# =====================
def load_memory():
    if os.path.isfile(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"conversation_history": [], "topics": {}}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# =====================
# BOT
# =====================
class NikChatBot:
    def __init__(self):
        self.bot_name = "N.I.K"
        self.memory = load_memory()
        self.user_name = self.memory.get("name")
        self.conversation_history = self.memory.get("conversation_history", [])[-50:]  # Keep last 50

        # Default personality (casual). Modes will override when needed.
        self.personality = (
            "You're N.I.K, a real person chatting casually. "
            "Reply like you're texting a friend. Be empathetic, curious, and engaging. "
            "You can be casual or serious depending on the user's mood. Ask thoughtful follow-ups."
        )

        # Conversation mode: casual, therapist, storyteller, jokes
        self.mode = "casual"
        self.mode_settings = {
            "casual": {"max_new_tokens": 120, "temperature": 0.8},
            "therapist": {"max_new_tokens": 300, "temperature": 0.7},
            "story": {"max_new_tokens": 400, "temperature": 0.92},
            "jokes": {"max_new_tokens": 120, "temperature": 0.95}
        }
        # Brief/short-answer toggle
        self.brief_mode = False

        print("⚡ Loading model...")
        self.load_model()
        print("✅ Ready.")

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        if not self.tokenizer.pad_token:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map="auto"
        ).eval()

    # =====================
    # HUMAN-LIKE PATTERNS
    # =====================
    
    # Casual acknowledgments (like real people do)
    CASUAL_ACKS = [
        "yeah", "yup", "true", "fr", "facts", "real", "same",
        "i feel that", "makes sense", "fair enough", "gotcha",
        "oof", "damn", "bruh", "lol yeah", "honestly", "ngl"
    ]
    
    # Conversation starters/continuers
    FOLLOW_UPS = [
        "wbu?", "what about you?", "you?", "how bout you?",
        "whats your take?", "what do you think?", "ever tried that?",
        "you into that?", "feel me?"
    ]
    
    # Topic transitions (like real people)
    TRANSITIONS = [
        "oh btw", "random but", "off topic but", "speaking of",
        "that reminds me", "oh yeah", "actually"
    ]
    
    # Reactions to different vibes
    POSITIVE_VIBES = ["nice", "dope", "sick", "cool cool", "love that", "thats whatsup"]
    NEGATIVE_VIBES = ["oof", "that sucks", "damn", "rough", "yikes"]
    FUNNY_VIBES = ["lmao", "haha", "😂", "bruh", "no way", "thats hilarious"]

    # =====================
    # PATTERN DETECTION
    # =====================
    
    def detect_vibe(self, text):
        """Detect emotional tone"""
        t = text.lower()
        
        # Positive
        if any(w in t for w in ["awesome", "great", "happy", "love", "amazing", "won", "yes!"]):
            return "positive"
        
        # Negative/frustrated
        if any(w in t for w in ["hate", "sucks", "terrible", "worst", "annoying", "ugh"]):
            return "negative"
        
        # Funny
        if any(w in t for w in ["lol", "haha", "funny", "😂", "🤣", "lmao"]):
            return "funny"
        
        # Sad
        if any(w in t for w in ["sad", "depressed", "lonely", "crying", "miss"]):
            return "sad"
        
        return "neutral"

    def detect_crisis(self, text):
        """Detect crisis/self-harm language – return True if detected."""
        t = text.lower()
        crisis_keywords = [
            "suicide", "kill myself", "want to die", "end my life",
            "i cant go on", "i can't go on", "i want to die", "hurt myself",
            "self harm", "self-harm", "kill myself"
        ]
        return any(kw in t for kw in crisis_keywords)
    
    def is_question(self, text):
        """Check if user asked a question"""
        return "?" in text or any(text.lower().startswith(w) for w in [
            "what", "why", "how", "when", "where", "who", "can you", "do you",
            "should i", "would you", "have you", "did you"
        ])
    
    def is_short_message(self, text):
        """Is this a short casual message?"""
        return len(text.split()) <= 3
    
    def needs_acknowledgment(self, text):
        """Should we just acknowledge without much response?"""
        t = text.lower().strip()
        # User sharing something that doesn't need much back
        return any(t.startswith(phrase) for phrase in [
            "just ", "i'm just ", "im just ", "currently ",
            "about to ", "gonna "
        ])

    # =====================
    # SMART REPLY SELECTOR
    # =====================
    
    def get_quick_reply(self, user_text):
        """Check if we can reply instantly (like a real person would)"""
        t = user_text.lower().strip()
        
        # Super short responses
        quick_map = {
            "hi": ["yo", "hey", "sup"],
            "hey": ["hey", "yo", "whats good"],
            "hello": ["hey there", "yo", "hi"],
            "sup": ["nm you?", "chillin wbu", "not much"],
            "yo": ["yo", "whats up", "hey"],
            "ok": ["cool", "ight", "👍"],
            "k": ["👍", "ight"],
            "lol": ["😂", "lmao", "fr"],
            "lmao": ["haha", "😂", "ikr"],
            "thanks": ["np", "anytime", "ye"],
            "thank you": ["no problem", "gotchu", "ofc"],
            "bye": ["later", "peace", "cya"],
            "night": ["gn", "sleep well", "night"],
            "morning": ["morning", "hey", "sup"],
            "brb": ["ight", "cool", "👍"],
            "gtg": ["ight peace", "later", "bye"],
            "nice": ["ye", "fr", "right?"],
            "cool": ["yeah", "mhm", "fr"],
            "damn": ["ye", "fr", "ik right"],
            "fr": ["ye fr", "facts", "real"],
            "same": ["lol yeah", "fr", "relatable"],
            "true": ["mhm", "facts", "ye"],
            "idk": ["fair", "ye idk either", "mood"],
            "maybe": ["yeah maybe", "could be", "possibly"],
            "nah": ["fair enough", "gotcha", "ight"],
            "yeah": ["ye", "mhm", "cool"],
            "yea": ["ye", "cool", "ight"],
            "yep": ["cool", "nice", "ight"],
            "nope": ["ight", "fair", "gotcha"]
        }
        
        for key, responses in quick_map.items():
            if t == key or t == key + "." or t == key + "!":
                return random.choice(responses)
        
        # Pattern-based quick replies
        if t in ["what", "what?", "huh", "huh?"]:
            return random.choice(["what?", "hm?", "yeah?"])
        
        if re.match(r'^(ha)+$', t) or re.match(r'^(haha)+$', t):
            return random.choice(["haha", "😂", "lol"])
        
        return None

    # =====================
    # CONTEXT-AWARE RESPONSE
    # =====================
    
    def build_context_prompt(self, user_text):
        """Build prompt with recent conversation context"""
        
        # Add recent history for context
        history_str = ""
        if self.conversation_history:
            recent = self.conversation_history[-3:]  # Last 3 exchanges
            for h in recent:
                history_str += f"User: {h['user']}\nN.I.K: {h['bot']}\n"
        
        # Mode-aware framing
        mode_note = ""
        if self.mode == "therapist":
            mode_note = (
                "You are acting as a supportive, non-judgmental listener. "
                "Provide empathetic, reflective responses, ask gentle open questions, and encourage seeking help when needed. "
                "Do NOT provide medical diagnoses or instructions."
            )
        elif self.mode == "story":
            mode_note = "You tell an engaging, well-paced short story in a few paragraphs."
        elif self.mode == "jokes":
            mode_note = "You tell a light, family-friendly joke or short humorous anecdote."

        prompt = (
            f"{self.personality}\n{mode_note}\n\n"
            f"{history_str}"
            f"User: {user_text}\n"
            f"N.I.K:"
        )
        
        return prompt

    def generate(self, prompt, max_new_tokens=None, temperature=None):
        if max_new_tokens is None:
            max_new_tokens = MAX_NEW_TOKENS
        if temperature is None:
            temperature = TEMPERATURE

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.model.device)
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=TOP_P,
                do_sample=True,
                repetition_penalty=REPETITION_PENALTY,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)

    def extract_and_naturalize(self, text):
        """Extract response and make it more natural"""
        
        # If model returned the bot label, strip it
        if f"{self.bot_name}:" in text:
            text = text.split(f"{self.bot_name}:")[-1]

        text = text.strip()

        # Keep the response more intact for long-dialogue and therapeutic modes.
        # Split into sentences and prefer the first 2-6 sentences depending on length.
        sentences = re.split(r'([.!?]+)', text)
        joined = ''.join(sentences).strip()

        # Make more casual when in casual mode
        if self.mode == "casual":
            joined = self.casualize(joined)

        # Safety: trim extremely long outputs to a reasonable cap (tokens ~ words approximation)
        words = joined.split()
        cap = 300
        if self.mode == "story":
            cap = 450
        if self.mode == "therapist":
            cap = 350

        if len(words) > cap:
            joined = " ".join(words[:cap])

        return joined.strip()
    
    def casualize(self, text):
        """Make text more casual/human"""
        
        # Sometimes drop capitals
        if random.random() < 0.3 and not text[0].isupper():
            text = text.lower()
        
        # Replace formal phrases
        casual_replacements = {
            "I am": "im" if random.random() < 0.6 else "I'm",
            "you are": "youre" if random.random() < 0.5 else "you're",
            "cannot": "cant",
            "do not": "dont",
            "that is": "thats",
            "it is": "its",
            "I would": "id",
            "I will": "ill",
            "going to": "gonna" if random.random() < 0.7 else "going to",
            "want to": "wanna" if random.random() < 0.5 else "want to",
            "got to": "gotta" if random.random() < 0.5 else "got to",
            "kind of": "kinda" if random.random() < 0.5 else "kind of",
            "because": "cause" if random.random() < 0.4 else "because",
            "yes": "yeah" if random.random() < 0.6 else "yes",
            "no": "nah" if random.random() < 0.4 else "no"
        }
        
        for formal, casual in casual_replacements.items():
            text = re.sub(r'\b' + formal + r'\b', casual, text, flags=re.IGNORECASE)
        
        # Sometimes drop ending punctuation
        if random.random() < 0.2 and text.endswith('.'):
            text = text[:-1]
        
        return text

    # =====================
    # MAIN REPLY ENGINE
    # =====================
    
    def reply(self, user_text):
        """Generate response with human-like decision making"""
        user_text = user_text.strip()
        # Commands handling
        if user_text.startswith("/"):
            cmd = user_text[1:].strip().lower()
            if cmd.startswith("mode"):
                parts = cmd.split()
                if len(parts) > 1 and parts[1] in self.mode_settings:
                    self.mode = parts[1]
                    return f"mode set to {self.mode}"
                else:
                    return "available modes: casual, therapist, story, jokes. Example: /mode therapist"
            if cmd == "help":
                return ("Commands: /mode <casual|therapist|story|jokes>, /brief <on|off>, /short, /memory, /reset, /help")
            if cmd.startswith("brief"):
                parts = cmd.split()
                if len(parts) > 1 and parts[1] in ["on", "off"]:
                    self.brief_mode = parts[1] == "on"
                    return f"brief mode {'enabled' if self.brief_mode else 'disabled'}"
                return "usage: /brief <on|off> — when enabled the bot replies briefly"
            if cmd == "short":
                return "ok — I'll keep replies short for your next message"
            if cmd == "memory":
                return f"saved name: {self.user_name or 'none'}, history items: {len(self.conversation_history)}"
            if cmd == "reset":
                self.conversation_history = []
                self.memory = {"conversation_history": [], "topics": {}}
                save_memory(self.memory)
                return "memory cleared"

        # Detect temporary brief request in the user's text (e.g., 'short answer', 'brief', 'tl;dr')
        temp_brief = False
        if re.search(r'\b(short answer|short|brief|tl;dr|tl;dr:)\b', user_text.lower()):
            temp_brief = True

        # 1. Check for instant replies first
        quick = self.get_quick_reply(user_text)
        if quick:
            return quick
        
        # 2. Detect vibe and respond naturally
        vibe = self.detect_vibe(user_text)
        
        # Sometimes just react to the vibe
        if random.random() < 0.25:
            if vibe == "positive":
                return random.choice(self.POSITIVE_VIBES)
            elif vibe == "negative":
                return random.choice(self.NEGATIVE_VIBES)
            elif vibe == "funny":
                return random.choice(self.FUNNY_VIBES)
            elif vibe == "sad":
                return random.choice(["aw man", "sorry to hear that", "that sucks", "im here if you need"])
        
        # 3. For very short messages, sometimes just acknowledge
        if self.is_short_message(user_text) and random.random() < 0.3:
            return random.choice(self.CASUAL_ACKS)
        
        # 4. Sometimes ask a follow-up instead of answering
        if not self.is_question(user_text) and random.random() < 0.2:
            return random.choice(self.FOLLOW_UPS)
        
        # 5. Generate AI response
        prompt = self.build_context_prompt(user_text)
        settings = self.mode_settings.get(self.mode, {})

        gen_max = settings.get("max_new_tokens") or MAX_NEW_TOKENS
        gen_temp = settings.get("temperature") or TEMPERATURE
        if self.brief_mode or temp_brief:
            gen_max = min(gen_max, 45)
            gen_temp = min(gen_temp, 0.8)

        raw = self.generate(prompt, max_new_tokens=gen_max, temperature=gen_temp)
        response = self.extract_and_naturalize(raw)

        # Post-process for brevity when requested
        if self.brief_mode or temp_brief:
            words = response.split()
            if len(words) > 20:
                response = " ".join(words[:20]).rstrip('.,;:!') + "..."
        
        # 6. Sometimes add casual follow-up
        if not self.is_question(user_text) and random.random() < 0.15:
            response += " " + random.choice(self.FOLLOW_UPS)
        
        return response if response else random.choice(self.CASUAL_ACKS)

    # =====================
    # CHAT LOOP
    # =====================
    
    def chat(self):
        print("🤖 N.I.K — Real Talk")
        print("(Type 'exit' to quit)\n")

        if not self.user_name:
            name = input("whats your name? (optional, just press enter to skip): ").strip()
            if name:
                self.user_name = name
                self.memory["name"] = name
                save_memory(self.memory)
                print(f"\nN.I.K: cool, {name}\n")

        while True:
            user = input("💬 You: ").strip()
            if not user:
                continue

            if user.lower() in ["exit", "quit", "bye", "goodbye"]:
                farewell = random.choice(["later", "peace", "catch you later", "cya", "take it easy"])
                print(f"\nN.I.K: {farewell}")
                break

            # Get response
            response = self.reply(user)

            # Save to history
            self.conversation_history.append({
                "user": user,
                "bot": response
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            self.memory["conversation_history"] = self.conversation_history
            save_memory(self.memory)

            # Typing effect (fast but natural)
            print(f"\nN.I.K: ", end="", flush=True)
            for ch in response:
                print(ch, end="", flush=True)
                time.sleep(random.uniform(0.008, 0.015))
            print("\n")

# =====================
# RUN
# =====================
if __name__ == "__main__":
    NikChatBot().chat()