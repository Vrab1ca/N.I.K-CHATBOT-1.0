import speech_recognition as sr
import pyttsx3
import time

from nik_chatbot import NikBrain   # 🔗 CONNECT TO AI BRAIN

# -------------------
# VOICE ENGINE
# -------------------
engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.setProperty("volume", 0.9)

voices = engine.getProperty("voices")

# choose first voice (change index if you want)
engine.setProperty("voice", voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# -------------------
# SPEECH TO TEXT
# -------------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

# -------------------
# AI BRAIN
# -------------------
bot = NikBrain()

print("🎤 Voice bot ready. Say something... (Ctrl+C to exit)")

while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(source)

        print("🧠 Listening...")
        user_text = recognizer.recognize_google(audio)
        print(f"👤 You: {user_text}")

        reply = bot.reply(user_text)
        print(f"🤖 N.I.K: {reply}")

        speak(reply)
        time.sleep(0.2)

    except sr.UnknownValueError:
        print("🤔 Didn't catch that.")
    except KeyboardInterrupt:
        print("\n👋 Exiting voice chat.")
        break
    except Exception as e:
        print("❌ Error:", e)