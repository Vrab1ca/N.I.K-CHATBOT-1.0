#!/usr/bin/env python3
"""
N.I.K — Fast, chill, human-like chatbot
Optimized for:
 - Speed
 - Natural chat flow
 - Real person vibe
"""

import os
import time
import json
import random
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# =====================
# CONFIG (SPEED FIRST)
# =====================
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
MEMORY_FILE = "nik_memory.json"

MAX_NEW_TOKENS = 60      # FAST
TEMPERATURE = 0.7
TOP_P = 0.85
REPETITION_PENALTY = 1.1

# =====================
# QUICK CONTENT
# =====================
JOKES = [
    "Debugging is just arguing with your past self.",
    "My PC freezes more than my emotions.",
    "Programmers don’t sleep — they wait."
]

FACTS = [
    "Octopuses have three hearts.",
    "Honey never spoils.",
    "Bananas are berries."
]

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
    return {}

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

        self.personality = (
            "You are N.I.K, a calm, grounded, chill friend. "
            "You talk like a real human texting. "
            "Replies are short, natural, and relaxed. "
            "Never sound like an assistant. Never explain too much."
        )

        print("⚡ Loading model...")
        self.load_model()
        print("✅ Ready.")

    # =====================
    # MODEL
    # =====================
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
    # FAST HUMAN REPLIES
    # =====================
    FAST_REPLIES = {
        "ok": ["Alright.", "Yeah.", "Got it."],
        "lol": ["😄", "Haha.", "Yeah lol."],
        "thanks": ["Anytime.", "No problem.", "👍"],
        "yo": ["Yo.", "What’s up?", "Hey."],
        "sup": ["Chillin. You?", "Not much. You?"],
        "hi": ["Hey.", "Yo.", "Hey there."]
    }

    ACKS = ["Yeah.", "I see.", "Makes sense.", "Gotcha."]

    # =====================
    # EMOTION
    # =====================
    def detect_anger(self, text):
        t = text.lower()
        if any(p in t for p in ["i hate", "this is bullshit", "i'm done"]):
            return "strong"
        if any(w in t for w in ["wtf", "damn", "shit"]):
            return "mild"
        return None

    def detect_sad(self, text):
        return any(w in text.lower() for w in ["sad", "lonely", "depressed", "hopeless"])

    # =====================
    # PROMPT (MINIMAL)
    # =====================
    def build_prompt(self, user_text):
        return (
            f"{self.personality}\n\n"
            f"User: {user_text}\n"
            f"{self.bot_name}:"
        )

    # =====================
    # GENERATION
    # =====================
    def generate(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                do_sample=True,
                repetition_penalty=REPETITION_PENALTY,
                pad_token_id=self.tokenizer.eos_token_id
            )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)

    def extract(self, text):
        if f"{self.bot_name}:" in text:
            text = text.split(f"{self.bot_name}:")[-1]

        text = text.replace("\n", " ").strip()
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        result = ". ".join(sentences[:2])

        if not result.endswith((".", "!", "?")):
            result += "."

        if len(result.split()) > 30:
            result = " ".join(result.split()[:30]) + "."

        return result

    # =====================
    # MAIN REPLY LOGIC
    # =====================
    def reply(self, user_text):
        t = user_text.lower().strip()

        # Instant replies
        if t in self.FAST_REPLIES:
            return random.choice(self.FAST_REPLIES[t])

        # Content
        if "joke" in t:
            return random.choice(JOKES)
        if "fact" in t:
            return random.choice(FACTS)

        # Emotions
        anger = self.detect_anger(user_text)
        if anger == "strong":
            return random.choice([
                "Alright, slow down. What happened?",
                "Yeah, that sounds rough."
            ])
        if anger == "mild":
            return random.choice(["Sounds annoying.", "Yeah, I feel that."])

        if self.detect_sad(user_text):
            return "That’s heavy. I’m here if you wanna talk."

        # Acknowledgment (human behavior)
        if len(user_text.split()) > 6 and random.random() < 0.15:
            return random.choice(self.ACKS)

        # Model response
        prompt = self.build_prompt(user_text)
        raw = self.generate(prompt)
        return self.extract(raw)

    # =====================
    # CHAT LOOP
    # =====================
    def chat(self):
        print("🤖 N.I.K — Chill Chat")

        if not self.user_name:
            name = input("Your name (optional): ").strip()
            if name:
                self.user_name = name
                self.memory["name"] = name
                save_memory(self.memory)

        while True:
            user = input("\n💬 You: ").strip()
            if not user:
                continue

            if user.lower() in ["exit", "quit", "bye"]:
                print("\nN.I.K: Alright, take it easy.")
                break

            response = self.reply(user)

            # Typing effect (FAST)
            print("\nN.I.K: ", end="", flush=True)
            for ch in response:
                print(ch, end="", flush=True)
                time.sleep(random.uniform(0.005, 0.012))
            print()

# =====================
# RUN
# =====================
if __name__ == "__main__":
    NikChatBot().chat()
