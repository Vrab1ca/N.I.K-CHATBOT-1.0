import speech_recognition as sr
import pyttsx3
import time
import random

from nikbrain import NikBrain   # CONNECT TO BRAIN

# -------------------
# VOICE ENGINE
# -------------------
engine = pyttsx3.init()
engine.setProperty("rate", 160)      # slower = more human
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

# Try different voices if available
engine.setProperty("voice", voices[0].id)

def speak(text):
    # small pauses = human feeling
    for part in text.split("."):
        if part.strip():
            engine.say(part.strip())
            engine.runAndWait()
            time.sleep(0.15)

# -------------------
# SPEECH TO TEXT
# -------------------
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.7

mic = sr.Microphone()

# -------------------
# AI BRAIN
# -------------------
bot = NikBrain()

print("🎤 N.I.K Voice Bot ready. Talk to me. (Ctrl+C to exit)\n")

while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("🧠 Listening...")
            audio = recognizer.listen(source)

        user_text = recognizer.recognize_google(audio)
        print(f"👤 You: {user_text}")

        reply = bot.reply(user_text)
        print(f"🤖 N.I.K: {reply}")

        speak(reply)
        time.sleep(0.2)

    except sr.UnknownValueError:
        print("🤔 I didn’t catch that.")
    except KeyboardInterrupt:
        print("\n👋 Bye.")
        break
    except Exception as e:
        print("❌ Error:", e)