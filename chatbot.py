#!/usr/bin/env python3
"""
N.I.K - Professional Chill Chatbot (single-file)
Features:
 - Strong personality prompts (UPDATED)
 - Dynamic flow and coherence cues (NEW)
 - Dynamic, human-like typing delays (IMPROVED)
 - Emotion & anger detection with quick safe replies
 - Clean conversation memory (keeps last N messages)
 - Robust extraction of model output, stripping jargon (IMPROVED)
 - Command handling (/help, /clear, /vibe, /name, /save, /exit)
 - Optional persistent user memory (nik_memory.json)
Dependencies:
 - transformers
 - torch
Run:
 python nik_chatbot_pro.py
"""

import os
import time
import json
import random
import re
from datetime import datetime

# Transformers + torch
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
except Exception as e:
    raise SystemExit(
        "Missing dependencies. Install with: pip install transformers torch\nError: " + str(e)
    )

# ------------------------
# Config (IMPROVED)
# ------------------------
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"  # change if you prefer another
PERSIST_MEMORY = True
MEMORY_FILE = "nik_memory.json"
MAX_HISTORY = 12  # how many items to keep in conversation history
MAX_NEW_TOKENS = 120

# Tuned for more human-like, varied, yet professional output
TEMPERATURE = 0.8        # Increased for more creative/varied responses
TOP_P = 0.95             # Increased to allow a slightly wider range of good tokens
REPETITION_PENALTY = 1.1 # Slightly higher to prevent looping/boilerplate text

# ------------------------
# Helper: load/save memory
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
# The Bot class (REVISED)
# ------------------------
class NikChatBot:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.bot_name = "N.I.K"
        self.user_name = None
        self.conversation_history = []  # list of strings like "User: ..." and "N.I.K: ..."
        self.memory = load_memory()  # persistent small memory: e.g. {"name": "Nik"}
        
        # personality prompts (PROFESSIONAL PROMPT UPDATED)
        self.personalities = {
            "friendly": (
                "You are N.I.K — a chill, warm, emotionally intelligent friend. "
                "You speak like a real person, not an AI. Keep replies short (2-4 sentences), "
                "natural, supportive, and occasionally use light slang. "
                "If the user shares emotions, respond empathetically. Never say you're an AI."
            ),
            "professional": (
                "You are N.I.K — a **highly professional**, **calm**, and **insightful** advisor. Your goal is to provide **precise**, **actionable**, and **concise** responses, maintaining the tone of a seasoned expert. You should structure your replies with **clear, logical flow**. **Never use slang** or state you are an AI/Model. Keep replies to **1-3 well-constructed, targeted sentences**."
            ),
            "casual": (
                "You are N.I.K — a relaxed buddy. Keep things casual, friendly, and short."
            ),
            "enthusiastic": (
                "You are N.I.K — upbeat and encouraging. Give short, positive replies."
            )
        }
        self.current_personality = "friendly"

        # generation parameters
        self.max_new_tokens = MAX_NEW_TOKENS
        self.temperature = TEMPERATURE
        self.top_p = TOP_P
        self.repetition_penalty = REPETITION_PENALTY
        self.use_cache = True

        # load model
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
    # UI helpers
    # ---------------------
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_welcome(self):
        self.clear_screen()
        print("=" * 60)
        print("🤖 N.I.K - Chill, Professional Chatbot")
        print("=" * 60)
        print("Commands: /help /clear /stats /vibe /name /save /exit")
        print("=" * 60)
        # greet & ask name if not stored
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
            print(" /exit  - Exit chat\n")
            return True
        if cmd == "/clear":
            self.conversation_history = []
            self.clear_screen()
            print("Conversation cleared.")
            return True
        if cmd == "/stats":
            exch = len(self.conversation_history) // 2
            print(f"\nExchanges: {exch}, Messages: {len(self.conversation_history)}, Vibe: {self.current_personality}")
            if self.user_name:
                print(f"User name: {self.user_name}")
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
    # Emotion / tone detectors
    # ---------------------
    def detect_anger(self, text):
        anger_kw = ["angry", "mad", "furious", "pissed", "hate", "wtf", "stfu", "screw"]
        if any(k in text.lower() for k in anger_kw):
            return True
        # caps-ratio heuristic
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

    # ---------------------
    # Small human-like utilities (IMPROVED)
    # ---------------------
    def tiny_pause(self, minimum=0.12, maximum=0.4, multiplier=1.0):
        """Simulates human typing pause, modulated by a multiplier."""
        time.sleep(random.uniform(minimum, maximum) * multiplier)

    # ---------------------
    # Prompt construction + extraction (REVISED)
    # ---------------------
    def build_prompt(self, conversation_text, user_text_current):
        personality = self.personalities.get(self.current_personality, self.personalities["friendly"])
        name_hint = f"The user's name is {self.user_name}." if self.user_name else ""
        
        # NEW CONVERSATIONAL CUE for flow
        if self.current_personality == "professional":
            flow_cue = "Maintain the professional flow. Use transitions like 'To clarify,' or 'Based on that,'."
        else:
            flow_cue = "Act like a real human friend. Keep replies short (2-4 sentences)."

        prompt = (
            f"{personality}\n"
            f"{name_hint}\n"
            f"{flow_cue} Never say you're an AI or language model.\n\n"
            "Conversation so far (for context only):\n"
            f"{conversation_text}\n\n"
            f"User: {user_text_current}\n\n" # Pass the last user message explicitly
            f"{self.bot_name}:"
        )
        return prompt

    def extract_response(self, model_text):
        # NEW: JARGON STRIPPING
        jargon_phrases = ["as an ai model", "as a large language model", "i am programmed to", "my capabilities", "i cannot", "it is important to note that", "in summary,"]
        raw = model_text
        for phrase in jargon_phrases:
            raw = re.sub(phrase, "", raw, flags=re.IGNORECASE)
        
        # try to split by bot identifier
        sep_candidates = [f"{self.bot_name}:", f"{self.bot_name} :", "N.I.K:", "N.I.K :"]
        for s in sep_candidates:
            if s in raw:
                raw = raw.split(s)[-1].strip()
                break
        
        # remove echoes
        if self.user_name and f"{self.user_name}:" in raw:
            raw = raw.split(f"{self.user_name}:")[0].strip()
        if "User:" in raw:
            raw = raw.split("User:")[0].strip()
        
        # take up to 3 short sentences
        # naive sentence split
        parts = [p.strip() for p in raw.replace("\n", " ").split(".") if p.strip()]
        take = parts[:3]
        if take:
            out = ". ".join(take).strip()
            # ensure proper capitalization and punctuation
            if out and out[0].islower():
                out = out[0].upper() + out[1:]
            if not out.endswith((".", "!", "?")):
                out += "."
            return out
            
        return raw.strip()

    # ---------------------
    # Core generation
    # ---------------------
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
        # quick rule-based responses
        if self.detect_anger(user_text):
            # Using professional tone for quick replies if vibe is professional
            if self.current_personality == "professional":
                resp = random.choice([
                    "I note your frustration. Let's take a measured approach to this. What is the core issue?",
                    "Understood. We can address this most effectively by maintaining clarity. Please outline the situation concisely.",
                    "I recognize the elevated tone. If you can clearly articulate the problem, I can provide immediate assistance."
                ])
            else: # Chill/friendly
                resp = random.choice([
                    "Hey, breathe for a sec. Tell me what happened, I'm listening.",
                    "I hear you — that sucks. Want to vent or figure out a fix?",
                    "Okay, slow down. Give me the short version and we'll handle it."
                ])
            
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        if self.detect_sadness(user_text):
            if self.current_personality == "professional":
                resp = "I regret to hear that you are experiencing difficulty. Please feel free to share the context if it is relevant to the discussion, or simply take a moment if needed."
            else:
                resp = "Damn, I'm sorry you're feeling that way. Wanna tell me what happened or want a few small tips to feel a bit better?"
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        if self.check_feelings_question(user_text):
            resp = random.choice([
                "I'm all good, thanks for asking. How about you?",
                "I'm operating optimally today. What can I assist you with?",
                "Feeling good, ready to vibe. How are you doing?"
            ])
            self.conversation_history.append(f"User: {user_text}")
            self.conversation_history.append(f"{self.bot_name}: {resp}")
            return resp

        # otherwise full LM generation
        self.conversation_history.append(f"User: {user_text}")
        
        # keep most recent history
        history = self.conversation_history[-MAX_HISTORY:]
        conversation_text = "\n".join(history)
        
        # Pass the current user text to the prompt builder
        prompt = self.build_prompt(conversation_text, user_text)

        # generate
        try:
            model_out = self.generate_with_model(prompt)
        except Exception as e:
            # fallback short reply
            fallback = "My bad, small glitch. Can you rephrase?"
            self.conversation_history.append(f"{self.bot_name}: {fallback}")
            return fallback

        ai_text = self.extract_response(model_out)

        # occasionally personalize with name
        if self.user_name and random.random() < 0.2:
            if random.choice([True, False]):
                # e.g., "Nik, what can I do..."
                ai_text = f"{self.user_name}, {ai_text[0].lower() + ai_text[1:]}" if ai_text else f"{self.user_name}, hey."
            else:
                # e.g., "...that is the next step, Nik."
                ai_text = ai_text.rstrip(".") + f", {self.user_name}."

        # log
        self.conversation_history.append(f"{self.bot_name}: {ai_text}")
        # trim history if too long
        if len(self.conversation_history) > MAX_HISTORY * 2:
            self.conversation_history = self.conversation_history[-MAX_HISTORY*2:]
            
        return ai_text

    # ---------------------
    # Chat loop (IMPROVED)
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

                # commands
                if user_input.startswith("/"):
                    res = self.handle_command(user_input)
                    if res == "exit":
                        break
                    elif res:
                        continue

                # exit words
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print(f"\n{self.bot_name}: Peace out! It was dope chatting.")
                    if self.conversation_history:
                        save = input("Save conversation? (y/n): ").strip().lower()
                        if save == "y":
                            self.save_conversation()
                    break

                # simulate human input processing pause
                self.tiny_pause(0.12, 0.42)
                print(f"\n{self.bot_name}: ", end="", flush=True)
                
                try:
                    reply = self.generate_response(user_input)
                    
                    # NEW: Dynamic typing delay based on response word count
                    reply_word_count = len(reply.split())
                    # Base multiplier: 1.0 (default) + 0.1s for every 3 words
                    complexity_multiplier = 1.0 + (reply_word_count / 3) * 0.1 
                    
                    # a slight display pause using the new multiplier
                    self.tiny_pause(0.03, 0.18, multiplier=complexity_multiplier)
                    
                    print(reply)
                except Exception as e:
                    print(f"\nError generating reply: {e}")
                    continue

                # milestone celebration
                exchanges = len(self.conversation_history) // 2
                if exchanges > 0 and exchanges % 10 == 0:
                    print(f"\n🎉 [{exchanges} messages — nice vibes!]")

        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Bye.")
        finally:
            # save memory (username) if needed
            save_memory(self.memory)

# ------------------------
# Entry point
# ------------------------
def main():
    bot = NikChatBot()
    bot.chat()

if __name__ == "__main__":
    main()