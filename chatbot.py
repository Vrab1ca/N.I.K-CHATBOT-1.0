#!/usr/bin/env python3
"""
N.I.K - Professional Chill Chatbot with Content Variety
Features:
 - Jokes, stories, facts, news when conversation gets repetitive
 - Detects repetitive patterns and offers fresh content
 - All previous features maintained
"""

import os
import time
import json
import random
import re
from datetime import datetime
from collections import Counter

# Transformers + torch
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
except Exception as e:
    raise SystemExit(
        "Missing dependencies. Install with: pip install transformers torch\nError: " + str(e)
    )

# ------------------------
# Config
# ------------------------
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
PERSIST_MEMORY = True
MEMORY_FILE = "nik_memory.json"
MAX_HISTORY = 12
MAX_NEW_TOKENS = 120

TEMPERATURE = 0.8
TOP_P = 0.95
REPETITION_PENALTY = 1.1

# ------------------------
# Content Banks (NEW)
# ------------------------
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything! 😄",
    "I told my computer I needed a break... now it won't stop sending me Kit-Kat ads. 🍫",
    "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
    "What's a computer's favorite snack? Microchips! 💻",
    "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
    "What did one wall say to the other? I'll meet you at the corner! 🏠",
    "Why don't eggs tell jokes? They'd crack each other up! 🥚",
    "What do you call a fake noodle? An impasta! 🍝"
]

FACTS = [
    "Fun fact: Honey never spoils. Archaeologists found 3,000-year-old honey in Egyptian tombs that was still edible! 🍯",
    "Did you know? Octopuses have three hearts and blue blood! 🐙",
    "Random fact: Bananas are berries, but strawberries aren't! 🍌",
    "Cool fact: A group of flamingos is called a 'flamboyance'! 🦩",
    "Tech fact: The first computer mouse was made of wood in 1964! 🖱️",
    "Space fact: A day on Venus is longer than its year! 🪐",
    "Nature fact: Trees can communicate through underground fungal networks! 🌳",
    "History fact: Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid! 🏛️"
]

SHORT_STORIES = [
    "Quick story: A guy once paid $1M for a pizza with Bitcoin in 2010. Today those coins would be worth billions. Lesson? HODL your crypto, bro! 💰",
    "True story: In Japan, there's a town where deer roam freely and bow to tourists for food. It's called Nara, and it's wild! 🦌",
    "Random tale: A programmer once accidentally deleted an entire company's database. The backup? Also deleted. They rebuilt everything from scratch. Always backup your backups! 💾",
    "Cool story: A man in Norway discovered a Viking ship in his backyard while gardening. Just casually digging up history! ⚔️",
    "Real talk: Someone once sold a grilled cheese sandwich with 'Jesus' face on it for $28,000 on eBay. People are wild! 🥪"
]

NEWS_TOPICS = [
    "Tech news: AI models are getting smaller but smarter. Edge computing is the next big thing! 🤖",
    "Space news: Private companies are racing to build hotels in space. Tourism is going orbital! 🚀",
    "Health tip: Studies show taking short walks every hour boosts productivity by 30%. Get moving! 🚶",
    "Gaming news: VR technology is finally becoming affordable and mainstream in 2025! 🎮",
    "Climate news: Solar panels are now cheaper than coal in most countries. Green energy is winning! ☀️"
]

# ------------------------
# Helper functions
# ------------------------
def load_memory():
    if not PERSIST_MEMORY:
        return {}
    if os.path.isfile(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    if not PERSIST_MEMORY:
        return
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ------------------------
# The Bot class (ENHANCED)
# ------------------------
class NikChatBot:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.bot_name = "N.I.K"
        self.user_name = None
        self.conversation_history = []
        self.memory = load_memory()
        
        # NEW: Track content shown to avoid repeats
        self.shown_jokes = set()
        self.shown_facts = set()
        self.shown_stories = set()
        self.shown_news = set()
        
        # NEW: Track user message patterns for repetition detection
        self.recent_user_topics = []
        
        self.personalities = {
            "friendly": (
                "You are N.I.K — a chill, warm, emotionally intelligent friend. "
                "You speak like a real person, not an AI. Keep replies short (2-4 sentences), "
                "natural, supportive, and occasionally use light slang. "
                "If the user shares emotions, respond empathetically. Never say you're an AI."
            ),
            "professional": (
                "You are N.I.K — a **highly professional**, **calm**, and **insightful** advisor. "
                "Provide **precise**, **actionable**, and **concise** responses. "
                "Keep replies to **1-3 well-constructed sentences**."
            ),
            "casual": (
                "You are N.I.K — a relaxed buddy. Keep things casual, friendly, and short."
            ),
            "enthusiastic": (
                "You are N.I.K — upbeat and encouraging. Give short, positive replies."
            )
        }
        self.current_personality = "friendly"

        self.max_new_tokens = MAX_NEW_TOKENS
        self.temperature = TEMPERATURE
        self.top_p = TOP_P
        self.repetition_penalty = REPETITION_PENALTY
        self.use_cache = True

        print("🚀 Loading model... this may take a moment.")
        self.load_model()
        print("✅ Ready. Type /help for commands.")

    def load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if not self.tokenizer.pad_token:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                print("🔧 Model loaded on GPU.")
            else:
                print("🔧 Model loaded on CPU.")
            self.model.eval()
        except Exception as e:
            raise SystemExit(f"Failed to load model {self.model_name}: {e}")

    # ---------------------
    # NEW: Repetition Detection
    # ---------------------
    def detect_repetition(self, user_text):
        """Check if user is asking similar things repeatedly"""
        # Extract key words from user input
        words = [w.lower() for w in re.findall(r'\w+', user_text) if len(w) > 3]
        self.recent_user_topics.append(words)
        
        # Keep only last 5 messages
        if len(self.recent_user_topics) > 5:
            self.recent_user_topics.pop(0)
        
        # If less than 3 messages, no repetition yet
        if len(self.recent_user_topics) < 3:
            return False
        
        # Count common words across recent messages
        all_words = []
        for msg_words in self.recent_user_topics[-3:]:
            all_words.extend(msg_words)
        
        word_counts = Counter(all_words)
        # If same words appear 3+ times, likely repetitive
        repetitive_words = [w for w, count in word_counts.items() if count >= 3]
        
        return len(repetitive_words) > 0
    
    def check_content_request(self, text):
        """Check if user is asking for specific content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["joke", "funny", "laugh", "humor"]):
            return "joke"
        if any(word in text_lower for word in ["fact", "did you know", "tell me something", "random"]):
            return "fact"
        if any(word in text_lower for word in ["story", "tale", "tell me about"]):
            return "story"
        if any(word in text_lower for word in ["news", "latest", "update", "what's happening"]):
            return "news"
        
        return None
    
    def get_fresh_content(self, content_type):
        """Get content that hasn't been shown yet"""
        if content_type == "joke":
            available = [j for i, j in enumerate(JOKES) if i not in self.shown_jokes]
            if not available:
                self.shown_jokes.clear()  # Reset if all shown
                available = JOKES
            joke = random.choice(available)
            self.shown_jokes.add(JOKES.index(joke))
            return joke
        
        elif content_type == "fact":
            available = [f for i, f in enumerate(FACTS) if i not in self.shown_facts]
            if not available:
                self.shown_facts.clear()
                available = FACTS
            fact = random.choice(available)
            self.shown_facts.add(FACTS.index(fact))
            return fact
        
        elif content_type == "story":
            available = [s for i, s in enumerate(SHORT_STORIES) if i not in self.shown_stories]
            if not available:
                self.shown_stories.clear()
                available = SHORT_STORIES
            story = random.choice(available)
            self.shown_stories.add(SHORT_STORIES.index(story))
            return story
        
        elif content_type == "news":
            available = [n for i, n in enumerate(NEWS_TOPICS) if i not in self.shown_news]
            if not available:
                self.shown_news.clear()
                available = NEWS_TOPICS
            news = random.choice(available)
            self.shown_news.add(NEWS_TOPICS.index(news))
            return news
        
        return None

    # ---------------------
    # UI helpers
    # ---------------------
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_welcome(self):
        self.clear_screen()
        print("=" * 60)
        print("🤖 N.I.K - Your Chill Bro with Stories & Facts")
        print("=" * 60)
        print("Commands: /help /clear /stats /vibe /name /save /exit")
        print("Ask me for: jokes, facts, stories, news!")
        print("=" * 60)
        if "name" in self.memory and self.memory["name"]:
            self.user_name = self.memory["name"]
            print(f"Welcome back, {self.user_name}!")
        else:
            name = input("What's your name? (press enter to skip): ").strip()
            if name:
                self.user_name = name
                self.memory["name"] = name
                save_memory(self.memory)
                print(f"Nice to meet you, {self.user_name}!")
            else:
                print("Cool — I'll call you buddy if needed.")
        print("=" * 60)

    # ---------------------
    # Commands
    # ---------------------
    def handle_command(self, cmd):
        cmd = cmd.lower().strip()
        if cmd == "/help":
            print("\nAvailable commands:")
            print(" /help  - Show this help")
            print(" /clear - Clear conversation history")
            print(" /stats - Show basic stats")
            print(" /vibe  - Change personality vibe")
            print(" /name  - Change your name")
            print(" /save  - Save conversation to file")
            print(" /exit  - Exit chat")
            print("\nContent requests:")
            print(" 'tell me a joke' - Get a random joke")
            print(" 'give me a fact' - Get a random fact")
            print(" 'tell me a story' - Get a short story")
            print(" 'any news?' - Get latest topic\n")
            return True
        if cmd == "/clear":
            self.conversation_history = []
            self.recent_user_topics = []
            self.clear_screen()
            print("Conversation cleared.")
            return True
        if cmd == "/stats":
            exch = len(self.conversation_history) // 2
            print(f"\nExchanges: {exch}, Messages: {len(self.conversation_history)}, Vibe: {self.current_personality}")
            if self.user_name:
                print(f"User name: {self.user_name}")
            print(f"Content shown: {len(self.shown_jokes)} jokes, {len(self.shown_facts)} facts, {len(self.shown_stories)} stories")
            return True
        if cmd == "/vibe":
            print("\nChoose vibe:")
            keys = list(self.personalities.keys())
            for i, k in enumerate(keys, 1):
                mark = "👉" if k == self.current_personality else "  "
                print(f"{mark} {i}. {k}")
            ch = input("Pick 1-4: ").strip()
            try:
                idx = int(ch) - 1
                if 0 <= idx < len(keys):
                    self.current_personality = keys[idx]
                    print(f"Vibe set to: {self.current_personality}")
                else:
                    print("Invalid choice.")
            except Exception:
                print("Invalid input.")
            return True
        if cmd == "/name":
            name = input("Enter your name: ").strip()
            if name:
                self.user_name = name
                self.memory["name"] = name
                save_memory(self.memory)
                print(f"Name saved as: {self.user_name}")
            return True
        if cmd == "/save":
            self.save_conversation()
            return True
        if cmd == "/exit":
            return "exit"
        return False

    def save_conversation(self):
        if not self.conversation_history:
            print("No conversation to save.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"nik_chat_{ts}.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("CHAT LOG - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                f.write("=" * 60 + "\n\n")
                for line in self.conversation_history:
                    f.write(line + "\n")
            print(f"Saved to {fname}")
        except Exception as e:
            print("Failed to save:", e)

    # ---------------------
    # Emotion detectors
    # ---------------------
    def detect_anger(self, text):
        anger_kw = ["angry", "mad", "furious", "pissed", "hate", "wtf", "stfu", "screw"]
        if any(k in text.lower() for k in anger_kw):
            return True
        if len(text) > 6:
            caps = sum(1 for c in text if c.isupper())
            if caps / len(text) > 0.6:
                return True
        if "!!!" in text or "???" in text:
            return True
        return False

    def detect_sadness(self, text):
        sad_kw = ["sad", "depressed", "lonely", "hopeless", "suicid", "unhappy"]
        return any(k in text.lower() for k in sad_kw)

    def check_feelings_question(self, text):
        feels = ["how are you", "how do you feel", "how's your day", "are you okay"]
        t = text.lower()
        return any(k in t for k in feels)

    def tiny_pause(self, minimum=0.12, maximum=0.4, multiplier=1.0):
        time.sleep(random.uniform(minimum, maximum) * multiplier)

    # ---------------------
    # Prompt & extraction
    # ---------------------
    def build_prompt(self, conversation_text, user_text_current):
        personality = self.personalities.get(self.current_personality, self.personalities["friendly"])
        name_hint = f"The user's name is {self.user_name}." if self.user_name else ""
        
        if self.current_personality == "professional":
            flow_cue = "Maintain professional flow. Use transitions like 'To clarify,' or 'Based on that,'."
        else:
            flow_cue = "Act like a real human friend. Keep replies short (2-4 sentences)."

        prompt = (
            f"{personality}\n"
            f"{name_hint}\n"
            f"{flow_cue} Never say you're an AI or language model.\n\n"
            "Conversation so far:\n"
            f"{conversation_text}\n\n"
            f"User: {user_text_current}\n\n"
            f"{self.bot_name}:"
        )
        return prompt

    def extract_response(self, model_text):
        jargon_phrases = ["as an ai model", "as a large language model", "i am programmed to", 
                         "my capabilities", "i cannot", "it is important to note that", "in summary,"]
        raw = model_text
        for phrase in jargon_phrases:
            raw = re.sub(phrase, "", raw, flags=re.IGNORECASE)
        
        sep_candidates = [f"{self.bot_name}:", f"{self.bot_name} :", "N.I.K:", "N.I.K :"]
        for s in sep_candidates:
            if s in raw:
                raw = raw.split(s)[-1].strip()
                break
        
        if self.user_name and f"{self.user_name}:" in raw:
            raw = raw.split(f"{self.user_name}:")[0].strip()
        if "User:" in raw:
            raw = raw.split("User:")[0].strip()
        
        parts = [p.strip() for p in raw.replace("\n", " ").split(".") if p.strip()]
        take = parts[:3]
        if take:
            out = ". ".join(take).strip()
            if out and out[0].islower():
                out = out[0].upper() + out[1:]
            if not out.endswith((".", "!", "?")):
                out += "."
            return out
            
        return raw.strip()

    def generate_with_model(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
                repetition_penalty=self.repetition_penalty,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=self.use_cache,
                num_beams=1
            )
            decoded = self.tokenizer.decode(out[0], skip_special_tokens=True)
        return decoded

    def generate_response(self, user_text):
        # NEW: Check for specific content requests first
        content_request = self.check_content_request(user_text)
        if content_request:
            content = self.get_fresh_content(content_request)
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {content}")
            return content
        
        # NEW: Detect repetitive conversation and offer variety
        if self.detect_repetition(user_text) and random.random() < 0.4:
            variety_options = ["joke", "fact", "story", "news"]
            content_type = random.choice(variety_options)
            content = self.get_fresh_content(content_type)
            intro = random.choice([
                "Yo, let's switch it up! ",
                "Here's something different: ",
                "Btw, check this out: ",
                "Random but cool: "
            ])
            resp = intro + content
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp
        
        # Quick emotion responses
        if self.detect_anger(user_text):
            if self.current_personality == "professional":
                resp = random.choice([
                    "I note your frustration. Let's take a measured approach. What is the core issue?",
                    "Understood. We can address this most effectively by maintaining clarity.",
                ])
            else:
                resp = random.choice([
                    "Hey, breathe for a sec. Tell me what happened, I'm listening.",
                    "I hear you — that sucks. Want to vent or figure out a fix?",
                ])
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        if self.detect_sadness(user_text):
            if self.current_personality == "professional":
                resp = "I regret to hear that. Please feel free to share if relevant."
            else:
                resp = "Damn, I'm sorry you're feeling that way. Wanna talk about it?"
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        if self.check_feelings_question(user_text):
            resp = random.choice([
                "I'm all good, thanks! How about you?",
                "Feeling good, ready to vibe. You good?",
                "I'm chill. What's up with you?"
            ])
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        # Full LM generation
        self.conversation_history.append(f"User: {user_text}")
        history = self.conversation_history[-MAX_HISTORY:]
        conversation_text = "\n".join(history)
        prompt = self.build_prompt(conversation_text, user_text)

        try:
            model_out = self.generate_with_model(prompt)
        except Exception as e:
            fallback = "My bad, small glitch. Can you rephrase?"
            self.conversation_history.append(f"{self.bot_name}: {fallback}")
            return fallback

        ai_text = self.extract_response(model_out)

        if self.user_name and random.random() < 0.2:
            if random.choice([True, False]):
                ai_text = f"{self.user_name}, {ai_text[0].lower() + ai_text[1:]}" if ai_text else f"{self.user_name}, hey."
            else:
                ai_text = ai_text.rstrip(".") + f", {self.user_name}."

        self.conversation_history.append(f"{self.bot_name}: {ai_text}")
        if len(self.conversation_history) > MAX_HISTORY * 2:
            self.conversation_history = self.conversation_history[-MAX_HISTORY*2:]
            
        return ai_text

    # ---------------------
    # Chat loop
    # ---------------------
    def chat(self):
        self.show_welcome()
        try:
            while True:
                self.tiny_pause(0.05, 0.15)
                prompt_text = f"{self.user_name}" if self.user_name else "You"
                user_input = input(f"\n💬 {prompt_text}: ").strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    res = self.handle_command(user_input)
                    if res == "exit":
                        break
                    elif res:
                        continue

                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print(f"\n{self.bot_name}: Peace out! It was dope chatting.")
                    if self.conversation_history:
                        save = input("Save conversation? (y/n): ").strip().lower()
                        if save == "y":
                            self.save_conversation()
                    break

                self.tiny_pause(0.12, 0.42)
                print(f"\n{self.bot_name}: ", end="", flush=True)
                
                try:
                    reply = self.generate_response(user_input)
                    reply_word_count = len(reply.split())
                    complexity_multiplier = 1.0 + (reply_word_count / 3) * 0.1 
                    self.tiny_pause(0.03, 0.18, multiplier=complexity_multiplier)
                    print(reply)
                except Exception as e:
                    print(f"\nError generating reply: {e}")
                    continue

                exchanges = len(self.conversation_history) // 2
                if exchanges > 0 and exchanges % 10 == 0:
                    print(f"\n🎉 [{exchanges} messages — nice vibes!]")

        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Bye.")
        finally:
            save_memory(self.memory)

def main():
    bot = NikChatBot()
    bot.chat()

if __name__ == "__main__":
    main()