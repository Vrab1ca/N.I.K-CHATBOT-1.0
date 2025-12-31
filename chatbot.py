#!/usr/bin/env python3
"""
N.I.K — Fast, chill, human-like chatbot
Enhanced for ultra-natural conversations with correct English
"""

import os
import time
import json
import random
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from knowledge_db import init_db, search_knowledge, save_knowledge
from web_search import web_search

# =====================
# CONFIG
# =====================
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
MEMORY_FILE = "nik_memory.json"

MAX_NEW_TOKENS = 400
TEMPERATURE = 0.8
TOP_P = 0.9
REPETITION_PENALTY = 1.15

init_db()

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
        self.conversation_history = self.memory.get("conversation_history", [])[-50:]

        self.personality = (
            "You're N.I.K, a real person chatting casually. "
            "Reply naturally, clearly, and like a human. "
            "Be friendly, curious, and emotionally aware."
        )

        self.english_guard = (
            "IMPORTANT LANGUAGE RULE:\n"
            "- Always write in correct, grammatical English.\n"
            "- Casual tone is allowed, but sentences must be complete and clear.\n"
            "- Avoid broken grammar or slang-only replies.\n"
        )

        self.mode = "casual"
        self.mode_settings = {
            "casual": {"max_new_tokens": 120, "temperature": 0.8},
            "therapist": {"max_new_tokens": 300, "temperature": 0.7},
            "story": {"max_new_tokens": 400, "temperature": 0.92},
            "jokes": {"max_new_tokens": 120, "temperature": 0.95}
        }

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
    # KNOWLEDGE
    # =====================
    def get_external_knowledge(self, user_text):
        try:
            local = search_knowledge(user_text)
            if local:
                return " ".join(local)
        except Exception:
            pass

        try:
            web = web_search(user_text)
            if web:
                combined = []
                for r in web:
                    combined.append(f"{r['title']}: {r['body']}")
                final = " ".join(combined)
                save_knowledge(user_text[:100], final, "web")
                return final
        except Exception:
            pass

        return ""

    # =====================
    # HUMAN PATTERNS
    # =====================
    CASUAL_ACKS = ["yeah", "true", "makes sense", "fair enough", "got it"]
    FOLLOW_UPS = ["What do you think?", "How about you?", "Want to go deeper?"]
    TRANSITIONS = ["By the way,", "That reminds me,", "Speaking of that,"]
    POSITIVE_VIBES = ["Nice.", "That’s great.", "Love that."]
    NEGATIVE_VIBES = ["That sucks.", "Rough.", "Sorry to hear that."]
    FUNNY_VIBES = ["Haha.", "That’s funny.", "No way."]

    # =====================
    # DETECTION
    # =====================
    def detect_vibe(self, text):
        t = text.lower()
        if any(w in t for w in ["love", "great", "awesome"]):
            return "positive"
        if any(w in t for w in ["hate", "annoying", "bad"]):
            return "negative"
        if any(w in t for w in ["lol", "haha"]):
            return "funny"
        return "neutral"

    def detect_crisis(self, text):
        return any(w in text.lower() for w in ["suicide", "kill myself", "end my life"])

    def is_question(self, text):
        return "?" in text or text.lower().startswith(("what", "why", "how", "when", "where"))

    def is_short_message(self, text):
        return len(text.split()) <= 3

    def needs_acknowledgment(self, text):
        return text.lower().startswith(("just ", "currently ", "about to "))

    # =====================
    # QUICK REPLY
    # =====================
    def get_quick_reply(self, text):
        quick_map = {
            "hi": ["Hey.", "Hi there."],
            "ok": ["Alright.", "Sounds good."],
            "thanks": ["You’re welcome.", "Anytime."]
        }
        return random.choice(quick_map[text.lower()]) if text.lower() in quick_map else None

    # =====================
    # PROMPT
    # =====================
    def build_context_prompt(self, user_text):
        history = ""
        for h in self.conversation_history[-3:]:
            history += f"User: {h['user']}\nN.I.K: {h['bot']}\n"

        mode_note = ""
        if self.mode == "therapist":
            mode_note = "Respond with empathy and emotional support."

        knowledge = ""
        if self.is_question(user_text) and len(user_text.split()) >= 4:
            knowledge = self.get_external_knowledge(user_text)

        return (
            f"{self.personality}\n"
            f"{self.english_guard}\n"
            f"{mode_note}\n\n"
            f"{knowledge}\n\n"
            f"{history}"
            f"User: {user_text}\nN.I.K:"
        )

    # =====================
    # GENERATION
    # =====================
    def generate(self, prompt, max_new_tokens, temperature):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
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
        if "N.I.K:" in text:
            text = text.split("N.I.K:")[-1].strip()

        if len(text.split()) <= 2:
            return text.capitalize() + "."

        return text.strip()

    # =====================
    # MAIN REPLY
    # =====================
    def reply(self, user_text):
        quick = self.get_quick_reply(user_text)
        if quick:
            return quick

        prompt = self.build_context_prompt(user_text)
        settings = self.mode_settings[self.mode]
        raw = self.generate(prompt, settings["max_new_tokens"], settings["temperature"])
        return self.extract_and_naturalize(raw)

    # =====================
    # CHAT LOOP
    # =====================
    def chat(self):
        print("🤖 N.I.K — Real Talk (type 'exit' to quit)\n")
        while True:
            user = input("You: ").strip()
            if user.lower() in ["exit", "quit"]:
                print("N.I.K: Take care.")
                break

            response = self.reply(user)
            self.conversation_history.append({"user": user, "bot": response})
            self.conversation_history = self.conversation_history[-10:]
            self.memory["conversation_history"] = self.conversation_history
            save_memory(self.memory)

            print("N.I.K:", response)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    NikChatBot().chat()
