#!/usr/bin/env python3
# voice.py — FIXED N.I.K Voice Bot (FAST SEARCH)

import re
import time
import unicodedata

import speech_recognition as sr
import pyttsx3

from nikbrain import NikBrain
from web_search_voice import search_wikipedia, search_web


# =========================
# VOICE ENGINE
# =========================
engine = pyttsx3.init()
engine.setProperty("rate", 195)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

def choose_voice(voices_list):
    for v in voices_list:
        name = v.name.lower()
        if "david" in name or "male" in name:
            return v.id
    return voices_list[0].id

engine.setProperty("voice", choose_voice(voices))


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
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.6
mic = sr.Microphone()


# =========================
# SMART SEARCH DETECTOR
# =========================
QUESTION_WORDS = [
    "what", "who", "when", "where", "why", "how",
    "explain", "tell me", "information", "info",
    "define", "about"
]

def needs_search(text):
    text = text.lower()
    if "?" in text:
        return True
    return any(word in text for word in QUESTION_WORDS)


def clean_query(text):
    text = text.lower()
    text = re.sub(r"(tell me|explain|information|info|about|what is|who is)", "", text)
    return text.strip()


# =========================
# AI BRAIN
# =========================
bot = NikBrain()

print("🎤 N.I.K Voice Bot READY (fixed). Speak.\n")


# =========================
# MAIN LOOP
# =========================
while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            print("🧠 Listening...")
            audio = recognizer.listen(source)

        user_text = recognizer.recognize_google(audio)
        print("👤 You:", user_text)

        reply = ""

        # ---------- SEARCH FIRST ----------
        if needs_search(user_text):
            query = clean_query(user_text)

            wiki = search_wikipedia(query)
            if wiki:
                reply = wiki
            else:
                web = search_web(query)
                reply = web

        # ---------- CHAT FALLBACK ----------
        if not reply:
            reply = bot.reply(user_text, style="fast")

        print("🤖 N.I.K:", reply)
        speak(reply)
        time.sleep(0.1)

    except sr.UnknownValueError:
        print("🤔 Didn't catch that.")
    except KeyboardInterrupt:
        print("\n👋 Bye.")
        break
    except Exception as e:
        print("❌ Error:", e)
