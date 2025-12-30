import re
import random
import speech_recognition as sr
import pyttsx3
import time

from nikbrain import NikBrain   # CONNECT TO BRAIN


# -------------------
# VOICE ENGINE
# -------------------
engine = pyttsx3.init()
# Base settings: slightly faster for a livelier voice
BASE_RATE = 180
engine.setProperty("rate", BASE_RATE)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

def choose_cool_boy_voice(voices_list):
    # Prefer common clear English voices on Windows (David/Zira/Michael), else fallback
    preferred = ["david", "zira", "michael", "mark", "male", "microsoft", "en_us", "en"]
    for p in preferred:
        for v in voices_list:
            name = getattr(v, 'name', '') or ''
            if p.lower() in name.lower():
                return v.id
            if hasattr(v, 'languages') and any(p.lower() in str(lang).lower() for lang in v.languages):
                return v.id
    # fallback to any male-like voice or first available
    for v in voices_list:
        if 'male' in (getattr(v, 'name', '') or '').lower():
            return v.id
    return voices_list[0].id if voices_list else None

chosen = choose_cool_boy_voice(voices)
if chosen:
    engine.setProperty("voice", chosen)


def _expand_initialisms(s: str) -> str:
    pattern = re.compile(r"\b(?:[A-Za-z]\.){2,}[A-Za-z]?\.?\b")
    def _repl(m):
        letters = [c for c in m.group(0) if c.isalpha()]
        return ' '.join(letters)
    return pattern.sub(_repl, s)


def speak(text, clarity='high', voice_style='cool_boy', speed='normal'):
    """Speak `text` with improved clarity and a cooler, less-robotic voice.

    - `clarity`: 'high' or 'normal' to control pauses.
    - `voice_style`: 'cool_boy' prefers a male voice and slightly faster, natural prosody.
    - `speed`: 'normal' or 'fast' to control playback rate and pause lengths.
    """
    if not text:
        return

    text = _expand_initialisms(text)
    text = re.sub(r"\s+", " ", text.strip())

    # Sentence split (keeps punctuation attached)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Pause settings (shorter when speed=='fast')
    if speed == 'fast':
        sentence_pause = 0.10
        comma_pause = 0.04
    else:
        if clarity == 'high':
            sentence_pause = 0.20
            comma_pause = 0.08
        else:
            sentence_pause = 0.12
            comma_pause = 0.05

    # Temporarily tweak engine properties for a less robotic feel
    prev_rate = engine.getProperty('rate')
    prev_voice = engine.getProperty('voice')

    if voice_style == 'cool_boy':
        base = BASE_RATE + 10
    else:
        base = BASE_RATE

    # Increase base rate for fast speed
    if speed == 'fast':
        base = min(320, base + 40)

    try:
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue

            # small natural variation in rate per sentence (keeps voice natural)
            rate_variation = random.randint(-6, 6)
            engine.setProperty('rate', max(120, base + rate_variation))

            # Speak the entire sentence at once (more reliable across platforms).
            # Adjust rate per-sentence, queue the sentence, then run the engine once.
            engine.say(s)
            engine.runAndWait()

            # Pause after each sentence for clarity (shorter if fast)
            time.sleep(sentence_pause)
    except Exception as e:
        print("TTS error:", e)
    finally:
        # restore previous settings
        try:
            engine.setProperty('rate', prev_rate)
            engine.setProperty('voice', prev_voice)
        except Exception:
            pass

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

        # request fast-style replies and speak them a bit faster
        reply = bot.reply(user_text, style='fast')
        print(f"🤖 N.I.K: {reply}")
        speak(reply, speed='fast', clarity='normal')
        time.sleep(0.2)

    except sr.UnknownValueError:
        print("🤔 I didn’t catch that.")
    except KeyboardInterrupt:
        print("\n👋 Bye.")
        break
    except Exception as e:
        print("❌ Error:", e)