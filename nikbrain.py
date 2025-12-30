import random
import re


class NikBrain:
    def __init__(self):
        self.last_topic = None
        self.user_name = None

        self.greetings = [
            "Yo. What’s good?",
            "Hey hey — what’s the vibe?",
            "What’s up? I’m here.",
            "Ay, talk to me.",
            "Hey. How you feeling today?",
            "Yo yo. What’s on your mind?",
            "Sup. Chill vibes only."
        ]

        self.jokes = [
            "Why don’t programmers like nature? Too many bugs.",
            "I tried to be normal once. Didn’t last.",
            "Debugging is just arguing with your past self.",
            "My brain has too many tabs open.",
            "Parallel lines got chemistry but no future. Sad."
        ]

        self.facts = [
            "Random fact: your brain burns a lot of energy just by thinking.",
            "Octopuses got three hearts. Built different.",
            "Your phone is stronger than the moon-landing computers. Crazy.",
            "Honey never expires. Immortal food."
        ]

        self.vibes = [
            "Vibe check. We going chill, funny, or deep?",
            "What’s the mood right now — music, talk, or chaos?",
            "Tell me the vibe and I’ll match it.",
            "Got a song stuck in your head?"
        ]

        self.default_lines = [
            "Yeah, I feel you.",
            "Lowkey makes sense.",
            "Ngl, that’s real.",
            "Hmm… interesting.",
            "I hear you.",
            "Go on, I’m listening.",
            "That’s valid.",
            "Not gonna lie, that hits."
        ]

        self.reactions = [
            "Fr.",
            "Facts.",
            "Honestly?",
            "Real talk.",
            "No cap."
        ]

        # extra slang, chill words and quick replies for vibe
        self.slang = [
            "lowkey", "highkey", "vibe", "chill", "dope", "lit", "bet", "bruh", "fam",
            "ya", "yeah", "ngl", "no cap", "fr", "imo", "irl"
        ]

        self.quick_responses = [
            "Bet.",
            "Say less.",
            "Gotcha.",
            "On it.",
            "Cool.",
            "Nice.",
            "I got you.",
            "Heard.",
            "Aight."
        ]

        self.chill_phrases = [
            "That’s vibes.",
            "Super chill.",
            "We vibin'.",
            "All good here.",
            "Easy breezy.",
            "Keep it mellow."
        ]

        self.typo_map = {
            "hello": ["helo", "helloo", "hallo"],
            "hello2": ["hi", "hey", "yo", "sup"],
            "how are you": ["how r u", "how ru", "hru"],
            "sorry": ["sry"],
            "i am": ["im", "i'm", "iam"]
        }

    def _clean(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s'?.!,]", " ", text)
        return text

    def _apply_style(self, resp, style):
        """Apply small stylistic tweaks: slang insertion, shorten for fast mode."""
        if not resp:
            return resp

        out = resp
        # fast style: prefer short quick responses
        if style == 'fast':
            if random.random() < 0.6:
                out = random.choice(self.quick_responses)
            else:
                # shorten long replies
                out_words = out.split()
                out = ' '.join(out_words[:6]) + ('' if len(out_words) <= 6 else '...')

        # chill/vibe style: sprinkle slang occasionally
        if style in ('chill', 'vibe') and random.random() < 0.45:
            token = random.choice(self.slang)
            # append or prepend small token for vibe
            if random.random() < 0.5:
                out = f"{token}, {out}"
            else:
                out = f"{out} — {token}"

        # small probability to append a chill phrase
        if style in ('chill', 'vibe') and random.random() < 0.18:
            out = f"{out} {random.choice(self.chill_phrases)}"

        return out

    def _matches(self, text, keywords):
        for k in keywords:
            if k in text:
                return True
            if k in self.typo_map:
                for alt in self.typo_map[k]:
                    if alt in text:
                        return True
        return False

    def _long_reply(self, parts, min_sent=2, max_sent=3):
        count = random.randint(min_sent, max_sent)
        chosen = random.sample(parts, min(count, len(parts)))
        if random.random() < 0.4:
            chosen.insert(0, random.choice(self.reactions))
        return " ".join(chosen)

    def reply(self, text, long=False, style='chill'):
        """Generate a reply.

        style: 'chill' (default), 'vibe', or 'fast' to influence wording and length.
        """
        text = self._clean(text)

        # GREETINGS
        if self._matches(text, ["hello", "hello2"]):
            resp = self._long_reply(self.greetings, 1, 2)
            return self._apply_style(resp, style)

        # HOW ARE YOU
        if self._matches(text, ["how are you"]):
            resp = "I’m chillin, honestly. Good energy, clear mind. You?"
            return self._apply_style(resp, style)

        # FEELINGS
        if any(x in text for x in ["sad", "depressed", "bad day", "unhappy", "lonely", "tired"]):
            self.last_topic = "feelings"
            parts = [
                "Damn… that sounds heavy.",
                "You don’t gotta carry it alone.",
                "If you wanna vent, I’m here.",
                "Or we can switch vibes if that helps."
            ]
            resp = self._long_reply(parts, 2, 3)
            return self._apply_style(resp, style)

        # JOKES
        if self._matches(text, ["joke", "funny"]):
            resp = random.choice(self.jokes)
            return self._apply_style(resp, style)

        # FACTS
        if self._matches(text, ["fact", "tell me something"]):
            resp = random.choice(self.facts)
            return self._apply_style(resp, style)

        # VIBE / MUSIC
        if any(x in text for x in ["vibe", "mood", "song", "music", "playlist"]):
            self.last_topic = "vibe"
            resp = self._long_reply(self.vibes, 1, 2)
            return self._apply_style(resp, style)

        # PROBLEMS
        if any(x in text for x in ["problem", "help", "fix", "issue"]):
            self.last_topic = "problem"
            parts = [
                "Alright, let’s break it down.",
                "Tell me what happened.",
                "We’ll fix it step by step, no stress."
            ]
            resp = self._long_reply(parts, 2, 3)
            return self._apply_style(resp, style)

        # CONTEXT FOLLOW-UP
        if self.last_topic == "feelings":
            resp = "I’m here. Take your time — what’s really bothering you?"
            return self._apply_style(resp, style)

        if self.last_topic == "problem":
            resp = "Okay. What’s the first thing that went wrong?"
            return self._apply_style(resp, style)

        # EXIT
        if any(x in text for x in ["bye", "exit", "stop", "goodbye"]):
            resp = "Aight. Stay safe and come back anytime."
            return self._apply_style(resp, style)

        # SHORT MESSAGES
        if len(text.split()) <= 3:
            prompts = [
                "Say more.",
                "Expand on that.",
                "What’s the vibe?",
                "Go on 👀"
            ]
            resp = random.choice(prompts)
            return self._apply_style(resp, style)

        # DEFAULT
        if long or random.random() < 0.3:
            resp = self._long_reply(
                self.default_lines + self.vibes + self.facts,
                2,
                3
            )
            return self._apply_style(resp, style)

        resp = random.choice(self.default_lines)
        return self._apply_style(resp, style)
