#!/usr/bin/env python3
# voice.py — Human-like Voice Search Bot

import re
import time
import unicodedata

import speech_recognition as sr
import pyttsx3

from nikbrain import NikBrain
from web_search_voice import smart_search


# =========================
# VOICE ENGINE
# =========================
engine = pyttsx3.init()
engine.setProperty("rate", 190)
engine.setProperty("volume", 1.0)

def speak(text):
    if not text:
        return
    text = unicodedata.normalize("NFKC", text)
    engine.say(text)
    engine.runAndWait()


# =========================
# SPEECH TO TEXT
# =========================
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
mic = sr.Microphone()


# =========================
# INTENT DETECTION
# =========================
def detect_intent(text):
    t = text.lower()
    if "history" in t:
        return "history"
    if any(w in t for w in ["what is", "explain", "information", "about"]):
        return "general"
    return "chat"


def extract_topic(text):
    return re.sub(
        r"(tell me|explain|what is|information|about|history of)",
        "",
        text.lower()
    ).strip()


# =========================
# BOT
# =========================
bot = NikBrain()

print("🎤 N.I.K is ready. Speak.\n")


# =========================
# MAIN LOOP
# =========================
while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source)

        user_text = recognizer.recognize_google(audio)
        print("👤 You:", user_text)

        intent = detect_intent(user_text)
        topic = extract_topic(user_text)

        if intent != "chat":
            mode = "short" if len(user_text) < 40 else "long"
            reply = smart_search(topic, intent, mode)
        else:
            reply = bot.reply(user_text, style="fast")

        print("🤖 N.I.K:", reply)
        speak(reply)
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n👋 Bye.")
        break
    except Exception as e:
        print("❌ Error:", e)
