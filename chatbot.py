#!/usr/bin/env python3
"""
N.I.K — Chill, grounded, human-like chatbot
Focus:
 - Calm, confident tone
 - No cringe, no forced slang
 - No overreaction to emotions
 - Short, natural replies
"""

import os
import time
import json
import random
import re
from datetime import datetime
from collections import Counter

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# ========================
# CONFIG
# ========================
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
MEMORY_FILE = "nik_memory.json"

MAX_HISTORY = 10
MAX_NEW_TOKENS = 120

TEMPERATURE = 0.75
TOP_P = 0.9
REPETITION_PENALTY = 1.1

# ========================
# CONTENT BANKS
# ========================
JOKES = [
    "Why do programmers hate nature? Too many bugs.",
    "I told my PC I needed space… now it won’t stop freezing.",
    "Debugging is just talking to yourself until the code listens."
]

FACTS = [
    "Octopuses have three hearts and blue blood.",
    "Honey never spoils. Ever.",
    "A day on Venus is longer than its year."
]

STORIES = [
    "A guy paid 10,000 Bitcoin for pizza in 2010. That pizza is legendary now.",
    "A programmer once fixed a bug by restarting the coffee machine. No one knows why."
]

NEWS = [
    "AI models are getting smaller but smarter.",
    "Solar energy is now cheaper than coal in most places."
]

# ========================
# MEMORY
# ========================
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

# ========================
# BOT
# ========================
class NikChatBot:
    def __init__(self):
        self.bot_name = "N.I.K"
        self.memory = load_memory()
        self.user_name = self.memory.get("name")

        self.history = []
        self.recent_topics = []

        self.personalities = {
            "friendly": (
                "You are N.I.K, a calm, grounded, chill friend. "
                "You speak like a real person, not an assistant. "
                "Replies are short (1–3 sentences). "
                "Be emotionally aware but never dramatic or preachy."
            ),
            "professional": (
                "You are N.I.K, a calm and professional advisor. "
                "Give short, clear, practical responses."
            )
        }

        self.current_personality = "friendly"

        print("🔧 Loading model...")
        self.load_model()
        print("✅ Ready. Type /help")

    # ====================
    # MODEL
    # ====================
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

    # ====================
    # EMOTION DETECTION
    # ====================
    def detect_anger(self, text):
        t = text.lower()

        strong = [
            "i hate", "i'm furious", "this is bullshit",
            "i'm done", "i'm pissed off"
        ]
        mild = ["wtf", "damn", "shit"]

        if any(s in t for s in strong):
            return "strong"
        if any(m in t for m in mild):
            return "mild"
        return None

    def detect_sadness(self, text):
        return any(w in text.lower() for w in ["sad", "lonely", "depressed", "hopeless"])

    # ====================
    # CONTENT CHECK
    # ====================
    def check_content(self, text):
        t = text.lower()
        if "joke" in t:
            return random.choice(JOKES)
        if "fact" in t:
            return random.choice(FACTS)
        if "story" in t:
            return random.choice(STORIES)
        if "news" in t:
            return random.choice(NEWS)
        return None

    # ====================
    # PROMPT
    # ====================
    def build_prompt(self, conversation, user_text):
        personality = self.personalities[self.current_personality]
        name_hint = f"The user's name is {self.user_name}." if self.user_name else ""

        return (
            f"{personality}\n"
            f"{name_hint}\n"
            "Never say you are an AI.\n\n"
            f"{conversation}\n"
            f"User: {user_text}\n"
            f"{self.bot_name}:"
        )

    # ====================
    # RESPONSE CLEANUP
    # ====================
    def soften_response(self, text):
        replacements = {
            "I regret to hear that": "That sucks",
            "Please feel free to share": "If you wanna talk, I’m here",
            "It is important to note": "",
            "In summary": ""
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text.strip()

    def extract_response(self, output):
        if f"{self.bot_name}:" in output:
            output = output.split(f"{self.bot_name}:")[-1]

        output = output.replace("\n", " ").strip()

        sentences = [s.strip() for s in output.split(".") if s.strip()]
        text = ". ".join(sentences[:2])

        if not text.endswith((".", "!", "?")):
            text += "."

        return text

    # ====================
    # GENERATION
    # ====================
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

    # ====================
    # MAIN LOGIC
    # ====================
    def reply(self, user_text):
        content = self.check_content(user_text)
        if content:
            return content

        anger = self.detect_anger(user_text)
        if anger == "strong":
            return random.choice([
                "Alright, let’s slow it down. What happened?",
                "Yeah, that sounds rough. Talk to me."
            ])
        if anger == "mild":
            return random.choice([
                "Sounds annoying. What’s up?",
                "Yeah, I feel that."
            ])

        if self.detect_sadness(user_text):
            return "That’s heavy. I’m here if you wanna talk."

        self.history.append(f"User: {user_text}")
        convo = "\n".join(self.history[-MAX_HISTORY:])

        prompt = self.build_prompt(convo, user_text)
        output = self.generate(prompt)

        text = self.extract_response(output)
        text = self.soften_response(text)

        if len(text.split()) > 35:
            text = " ".join(text.split()[:35]) + "."

        self.history.append(f"{self.bot_name}: {text}")
        return text

    # ====================
    # CHAT LOOP
    # ====================
    def chat(self):
        print("🤖 N.I.K — Chill Mode")
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
            time.sleep(random.uniform(0.1, 0.3))
            print(f"\nN.I.K: {response}")

# ========================
# RUN
# ========================
if __name__ == "__main__":
    NikChatBot().chat()
