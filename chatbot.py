#!/usr/bin/env python3
"""
N.I.K - Chill Chatbot
Improved full version of your FriendlyChatBot with more natural vibes,
better prompt engineering, robust extraction, emotion detection,
and small human-like timing to feel more 'real'.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from datetime import datetime
import os
import time
import random


class FriendlyChatBot:
    def __init__(self, model_name="microsoft/Phi-3-mini-4k-instruct"):
        self.model_name = model_name
        self.conversation_history = []
        self.max_history_length = 10  # keep a bit more context for continuity
        self.user_name = None
        self.bot_name = "N.I.K"

        # Speed / generation settings (tweak as needed)
        self.max_new_tokens = 120
        self.temperature = 0.7
        self.top_p = 0.9
        self.repetition_penalty = 1.08
        self.use_cache = True

        # More expressive, contextual personality prompts
        self.personalities = {
            "friendly": (
                "You are N.I.K — a chill, warm, supportive bro. "
                "Talk like a real person. Relaxed, positive, calm, and brief (2–4 sentences). "
                "Use light slang occasionally, never sound robotic or like an AI. "
                "If the user has a name, use it naturally sometimes."
            ),
            "professional": (
                "You are N.I.K — a calm, concise professional helper. "
                "Speak clearly, politely, and with short logical responses. "
                "No slang. No AI-style phrasing. Be efficient."
            ),
            "casual": (
                "You are N.I.K — a super chill buddy. "
                "Talk casual like a friendly person: warm, short, and natural. "
                "Use mild humor when appropriate, but keep it genuine."
            ),
            "enthusiastic": (
                "You are N.I.K — energetic and upbeat. "
                "Give short, encouraging replies, hype the user a little, and stay natural."
            )
        }
        self.current_personality = "casual"

        print("🚀 Loading N.I.K... (this may take a moment)")
        self.load_model()

    def load_model(self):
        """Load tokenizer and model with simple optimizations."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # If the model doesn't have pad_token defined, set it to eos
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                low_cpu_mem_usage=True
            )

            if torch.cuda.is_available():
                self.model = self.model.to('cuda')
                print("✅ Model loaded on GPU (faster!)")
            else:
                print("⚠️ Running on CPU (slower)")

            self.model.eval()
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise

    # --------------------------
    # Terminal / UI helpers
    # --------------------------
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_welcome(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("🤖 N.I.K - YOUR CHILL BRO CHATBOT (Improved)")
        print("=" * 60)
        print("\n💡 Commands:")
        print("  /help      - Show commands")
        print("  /clear     - Clear conversation history")
        print("  /stats     - Show stats")
        print("  /vibe      - Change N.I.K's vibe")
        print("  /name      - Set your name")
        print("  /save      - Save conversation to a file")
        print("  /exit      - End the chat")
        print("\n" + "=" * 60)

        name = input("\n😎 Yo! What's your name? (or Enter to skip): ").strip()
        if name:
            self.user_name = name
            print(f"\n🤙 Cool, {self.user_name}! I'm N.I.K, your chill bro.")
        else:
            print("\n👋 No worries! I'm N.I.K. Let's chat, bro!")

        print("\n💬 Just type whatever's on your mind!")
        print("=" * 60 + "\n")

    # --------------------------
    # Commands
    # --------------------------
    def handle_command(self, command):
        cmd = command.lower().strip()
        if cmd == "/help":
            print("\n📖 AVAILABLE COMMANDS:")
            print("  /help      - Show this help message")
            print("  /clear     - Clear conversation history")
            print("  /stats     - Show conversation statistics")
            print("  /vibe      - Change bot personality/vibe")
            print("  /name      - Change your name")
            print("  /save      - Save conversation to a text file")
            print("  /exit      - End the chat")
            return True

        if cmd == "/clear":
            self.conversation_history = []
            self.clear_screen()
            print("\n✨ Conversation history cleared! Fresh start.")
            return True

        if cmd == "/stats":
            exchanges = len(self.conversation_history) // 2
            print("\n📊 CONVERSATION STATS:")
            print(f"  💬 Exchanges: {exchanges}")
            print(f"  📝 Total messages: {len(self.conversation_history)}")
            print(f"  🎭 Personality: {self.current_personality}")
            if self.user_name:
                print(f"  👤 Your name: {self.user_name}")
            return True

        if cmd == "/vibe":
            print("\n🎭 CHOOSE N.I.K'S VIBE:")
            keys = list(self.personalities.keys())
            for i, k in enumerate(keys, 1):
                marker = "👉" if k == self.current_personality else "  "
                print(f"{marker} {i}. {k.title()}")
            choice = input("\nPick a number (1-4): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(keys):
                    self.current_personality = keys[idx]
                    print(f"\n✅ N.I.K's vibe set to: {self.current_personality}")
                else:
                    print("\n❌ Pick a valid number 1-4.")
            except ValueError:
                print("\n❌ Just enter a number.")
            return True

        if cmd == "/name":
            name = input("\n👤 Enter your name: ").strip()
            if name:
                self.user_name = name
                print(f"\n✅ Name updated to: {self.user_name}")
            else:
                print("\n❌ Name can't be empty.")
            return True

        if cmd == "/save":
            self.save_conversation()
            return True

        if cmd == "/exit":
            return "exit"

        return False

    # --------------------------
    # Persistence
    # --------------------------
    def save_conversation(self):
        if not self.conversation_history:
            print("\n⚠️ Nothing to save yet.")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{timestamp}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write(f"CHAT LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for msg in self.conversation_history:
                    f.write(msg + "\n\n")
            print(f"\n💾 Conversation saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving file: {e}")

    # --------------------------
    # Simple NLP detectors & helpers
    # --------------------------
    def check_feelings_question(self, user_input):
        feelings_keywords = [
            "how are you", "how do you feel", "how are you feeling",
            "are you okay", "are you happy", "are you sad",
            "what's your mood", "how's your day", "feeling good"
        ]
        user_lower = user_input.lower()
        return any(kw in user_lower for kw in feelings_keywords)

    def detect_anger_or_frustration(self, user_input):
        anger_keywords = [
            "angry", "mad", "furious", "pissed", "hate", "annoying", "stupid",
            "idiot", "dumb", "frustrating", "annoyed", "irritated", "fed up",
            "i'm done", "can't take", "so annoying", "drives me crazy",
            "pisses me off", "makes me mad", "really angry", "so frustrated"
        ]
        user_lower = user_input.lower()
        # Caps ratio
        if len(user_input) > 5:
            caps_ratio = sum(1 for c in user_input if c.isupper()) / len(user_input)
            if caps_ratio > 0.6:
                return True
        # punctuation
        if "!!!" in user_input or "??" in user_input:
            return True
        # keywords
        if any(kw in user_lower for kw in anger_keywords):
            return True
        return False

    def detect_sadness(self, user_input):
        sad_keywords = ["sad", "depressed", "lonely", "upset", "down", "suicid"]
        user_lower = user_input.lower()
        if any(kw in user_lower for kw in sad_keywords):
            return True
        return False

    # --------------------------
    # Prebuilt short support responses
    # --------------------------
    def generate_calming_response(self, user_input):
        person_keywords = ["boyfriend", "girlfriend", "friend", "partner", "husband",
                           "wife", "crush", "they", "he", "she", "guy", "girl"]
        is_about_person = any(kw in user_input.lower() for kw in person_keywords)
        if is_about_person:
            responses = [
                "Hey, breathe for a sec. I got you — what happened exactly?",
                "That's rough. Take a breath and tell me what went down.",
                "I feel you. Cool down a bit and then say what bothered you most.",
                "Damn, that's heavy. Start from the beginning, I'm listening."
            ]
        else:
            responses = [
                "Yo, I hear you bro. Take a breath. What's going on?",
                "That sucks, man. Tell me the short version so we can fix it.",
                "Okay, slow down — tell me what's the main thing bothering you.",
                "I got you. Want to vent or try to solve it now?"
            ]
        return random.choice(responses)

    def generate_feelings_response(self):
        responses = [
            "I'm chill, bro! Ready to vibe. How about you?",
            "Feeling relaxed and ready to help. You good?",
            "All good here — what's up with you?",
            "Chillin' and listening. Tell me what's on your mind."
        ]
        return random.choice(responses)

    def generate_helpful_hint(self):
        hints = [
            "💡 Tip: Try 'I feel...' instead of 'You always...' — it helps.",
            "💡 Try to cool off before responding. Give yourself 5 minutes.",
            "💡 Ask yourself: what do I actually want from this convo?",
            "💡 Writing the issue down can make the next step clearer."
        ]
        return random.choice(hints)

    # --------------------------
    # Core generation
    # --------------------------
    def build_prompt(self, recent_history):
        # Build a clear, instructive prompt
        personality = self.personalities[self.current_personality]
        name_hint = ""
        if self.user_name:
            name_hint = "If the user has a name, occasionally use it naturally."
        prompt = (
            f"{personality}\n"
            f"{name_hint}\n"
            "Act like a real person, not an AI. Keep replies short (2-4 sentences) and natural.\n"
            "Never say you are an AI. Keep the tone consistent with the personality.\n\n"
            "Conversation so far:\n"
            f"{recent_history}\n"
            f"{self.bot_name}:"
        )
        return prompt

    def extract_ai_response(self, model_output_text):
        """
        Extract the bot text after the last occurrence of the bot name token,
        and trim any accidental echoes of 'User:' or username.
        """
        # Prefer splitting by exact bot name token (N.I.K: or N.I.K :)
        # Use several possible separators robustly
        separators = [f"{self.bot_name}:", f"{self.bot_name} :", "N.I.K:", "N.I.K :"]
        raw = model_output_text
        for sep in separators:
            if sep in raw:
                raw = raw.split(sep)[-1].strip()
                break

        # Remove stuff after user echoes
        if self.user_name and f"{self.user_name}:" in raw:
            raw = raw.split(f"{self.user_name}:")[0].strip()
        if "User:" in raw:
            raw = raw.split("User:")[0].strip()

        # Keep only first few sentences (2-4) for concise output
        # Split into sentences by simple punctuation (not perfect but works practical)
        sentences = []
        parts = [p.strip() for p in raw.replace("\n", " ").split(".")]
        for p in parts:
            if p:
                sentences.append(p)
            if len(sentences) >= 3:
                break
        if sentences:
            cleaned = ". ".join(sentences).strip()
            if not cleaned.endswith("."):
                cleaned += "."
            return cleaned
        return raw

    def generate_response(self, user_input):
        """
        Main response generation wrapper.
        Uses rule-based short responses for emotions, otherwise prompts the LM.
        """
        # Quick rule-based handling (fast, human-feel)
        if self.detect_anger_or_frustration(user_input):
            ai_response = self.generate_calming_response(user_input)
            # if relationship flavored, append a tip sometimes
            if any(k in user_input.lower() for k in ["boyfriend", "girlfriend", "partner", "ex", "crush"]):
                ai_response = ai_response + " " + self.generate_helpful_hint()
            # log
            prefix = f"{self.user_name}: " if self.user_name else "User: "
            self.conversation_history.append(f"{prefix}{user_input}")
            self.conversation_history.append(f"{self.bot_name}: {ai_response}")
            return ai_response

        if self.check_feelings_question(user_input):
            ai_response = self.generate_feelings_response()
            prefix = f"{self.user_name}: " if self.user_name else "User: "
            self.conversation_history.append(f"{prefix}{user_input}")
            self.conversation_history.append(f"{self.bot_name}: {ai_response}")
            return ai_response

        if self.detect_sadness(user_input):
            # Sensitive, short, supportive — but not clinical
            ai_response = "Damn, I'm sorry you're feeling like that. Wanna tell me more or do you want a few quick tips to feel a bit better?"
            prefix = f"{self.user_name}: " if self.user_name else "User: "
            self.conversation_history.append(f"{prefix}{user_input}")
            self.conversation_history.append(f"{self.bot_name}: {ai_response}")
            return ai_response

        # Otherwise, ask the model
        prefix = f"{self.user_name}: " if self.user_name else "User: "
        self.conversation_history.append(f"{prefix}{user_input}")

        # Build recent history text
        recent_history = self.conversation_history[-self.max_history_length:]
        conversation_text = "\n".join(recent_history)

        prompt = self.build_prompt(conversation_text)

        # Tokenize and run model
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # Fast generation with sampling
        with torch.inference_mode():
            try:
                output = self.model.generate(
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
                answer = self.tokenizer.decode(output[0], skip_special_tokens=True)
            except Exception as e:
                # fallback short reply on failure
                print(f"\n❌ Model generation error: {e}")
                fallback = "My bad bro, had a glitch. Try rephrasing that?"
                self.conversation_history.append(f"{self.bot_name}: {fallback}")
                return fallback

        ai_response = self.extract_ai_response(answer)

        # Personalize with user's name sometimes
        if self.user_name and random.random() < 0.25:  # 25% chance to use the name
            # Put the name at the start or end naturally
            pos = random.choice(["start", "end"])
            if pos == "start":
                ai_response = f"{self.user_name}, {ai_response[0].lower() + ai_response[1:]}" if ai_response else f"{self.user_name}, hey."
            else:
                ai_response = ai_response.rstrip(".") + f", {self.user_name}."

        # Save to history
        self.conversation_history.append(f"{self.bot_name}: {ai_response}")

        return ai_response

    # --------------------------
    # Chat loop
    # --------------------------
    def chat(self):
        self.show_welcome()
        try:
            while True:
                prefix = f"{self.user_name}" if self.user_name else "You"
                user_input = input(f"\n💬 {prefix}: ").strip()
                if not user_input:
                    continue

                # Commands
                if user_input.startswith("/"):
                    result = self.handle_command(user_input)
                    if result == "exit":
                        break
                    elif result:
                        continue

                # Quick exit keywords
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print(f"\n{self.bot_name}: Peace out bro! It was dope chatting with you! 👋✨")
                    if len(self.conversation_history) > 0:
                        save = input("\n💾 Save our convo before you go? (y/n): ").lower()
                        if save == "y":
                            self.save_conversation()
                    break

                # Simulate a tiny human pause
                time.sleep(random.uniform(0.15, 0.4))

                # Generate reply
                print(f"\n{self.bot_name}: ", end="", flush=True)
                try:
                    response = self.generate_response(user_input)
                    # short display pause for realism
                    time.sleep(random.uniform(0.05, 0.25))
                    print(response)
                except KeyboardInterrupt:
                    print("\n\n👋 Chat interrupted. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Oops, something went wrong: {e}")
                    # Attempt to continue

                # Celebrate milestones
                exchanges = len(self.conversation_history) // 2
                if exchanges > 0 and exchanges % 10 == 0:
                    print(f"\n🎉 [{exchanges} messages! Nice vibes, bro!]")

        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")

# --------------------------
# Entrypoint
# --------------------------
def main():
    try:
        bot = FriendlyChatBot()
        bot.chat()
    except Exception as e:
        print(f"\n❌ Failed to start N.I.K: {e}")


if __name__ == "__main__":
    main()
