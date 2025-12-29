import re
import speech_recognition as sr
import pyttsx3
import time

from nikbrain import NikBrain   # CONNECT TO BRAIN


# -------------------
# VOICE ENGINE
# -------------------
engine = pyttsx3.init()
# Slightly slower rate for clarity but not too slow
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

def choose_clear_voice(voices_list):
    # Prefer common clear English voices on Windows (Zira/Anna/Microsoft), else fallback
    preferred = ["zira", "anna", "microsoft", "female", "en_US", "en"]
    for p in preferred:
        for v in voices_list:
            if v and getattr(v, 'name', None) and p.lower() in v.name.lower():
                return v.id
            # some voice objects expose languages
            if hasattr(v, 'languages') and any(p.lower() in str(lang).lower() for lang in v.languages):
                return v.id
    # fallback to first available
    return voices_list[0].id if voices_list else None

chosen = choose_clear_voice(voices)
if chosen:
    engine.setProperty("voice", chosen)


def speak(text, clarity='high'):
    """Speak `text` with improved clarity.

    - Splits on sentence end punctuation so each sentence is spoken distinctly.
    - Adds short pauses for commas and longer pauses between sentences.
    - `clarity` can be 'high' or 'normal' to control pause lengths.
    """
    if not text:
        return

    # Expand initialisms like "N.I.K." or "N.I.K" -> "N I K" so TTS reads each letter
    def _expand_initialisms(s: str) -> str:
        pattern = re.compile(r"\b(?:[A-Za-z]\.){2,}[A-Za-z]?\.?\b")
        def _repl(m):
            letters = [c for c in m.group(0) if c.isalpha()]
            return ' '.join(letters)
        return pattern.sub(_repl, s)

    text = _expand_initialisms(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text.strip())

    # Sentence split (keeps punctuation attached)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Pause settings
    if clarity == 'high':
        sentence_pause = 0.28
        comma_pause = 0.10
    else:
        sentence_pause = 0.16
        comma_pause = 0.06

    # Queue each sentence (keep punctuation) and run once to avoid truncation
    try:
        for sentence in sentences:
            if sentence.strip():
                engine.say(sentence.strip())
        engine.runAndWait()
        # small pause after full reply
        time.sleep(sentence_pause)
    except Exception as e:
        print("TTS error:", e)

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