import random
import re


class NikBrain:
    def __init__(self):
        self.last_topic = None
        self.user_name = None

        # expanded phrase lists for more varied, longer replies
        self.greetings = [
            "Hey. What’s good?",
            "Yo. How you doing?",
            "Hey hey. Talk to me.",
            "What’s up? I’m here for a chat.",
            "Hi there — tell me what’s on your mind."
        ]

        self.jokes = [
            "Why don’t programmers like nature? Too many bugs.",
            "I tried to be normal once. Worst two minutes of my life.",
            "Debugging is like being a detective in your own crime movie.",
            "Parallel lines have so much in common. It’s a shame they’ll never meet."
        ]

        self.facts = [
            "Fun fact: your brain uses about twenty percent of your body’s energy.",
            "Octopuses have three hearts. Wild, right?",
            "Your phone is more powerful than the computers used in the moon landing.",
            "Honey never spoils — archaeologists found edible honey in ancient tombs."
        ]

        self.vibes = [
            "I’m vibing. Want a chill topic or something hype?",
            "Vibe check: good music, good energy, or deep talk?",
            "Tell me a song you like and I’ll match the mood." 
        ]

        self.default_lines = [
            "Yeah, I feel that.",
            "Makes sense honestly.",
            "Go on. I’m listening.",
            "Hmm. Interesting.",
            "Not gonna lie, that’s real.",
            "That’s deep — tell me more about why you think that."
        ]

        # common misspellings / shorthand to tolerate
        self.typo_map = {
            "hello": ["helo", "helloo", "hallo"],
            "hello2": ["hi", "hey", "yo"],
            "how are you": ["how r u", "how ru", "howareyou"],
            "sorry": ["sry"],
            "i am": ["im", "i'm", "iam"]
        }

    def _clean(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s'?.!,]", " ", text)
        return text

    def _matches(self, text, keywords):
        # tolerant contains: match any keyword or common typo forms
        for k in keywords:
            if k in text:
                return True
            if k in self.typo_map:
                for alt in self.typo_map[k]:
                    if alt in text:
                        return True
        return False

    def _long_reply(self, parts, min_sent=2, max_sent=3):
        # join multiple short lines into a longer flowing reply
        count = random.randint(min_sent, max_sent)
        chosen = random.sample(parts, min(count, len(parts)))
        # make it a readable paragraph
        return " ".join(chosen)

    def reply(self, text, long=False):
        text_raw = text
        text = self._clean(text)

        # GREETINGS
        if self._matches(text, ["hello", "hello2"]):
            return self._long_reply(self.greetings, 1, 2) if long or random.random() < 0.3 else random.choice(self.greetings)

        # ASKING HOW I AM
        if "how are you" in text or self._matches(text, ["how are you"]):
            return "I’m chillin — feeling curious and ready to vibe. How about you?"

        # FEELINGS / MOOD
        if any(x in text for x in ["sad", "depressed", "bad day", "unhappy", "lonely"]):
            self.last_topic = "feelings"
            parts = [
                "Damn… that’s rough.",
                "If you want, tell me what happened — I can listen.",
                "Or if you prefer, we can distract with jokes, music, or a silly game."
            ]
            return self._long_reply(parts) if long or random.random() < 0.6 else random.choice(parts)

        # JOKES / FUN
        if self._matches(text, ["joke", "funny"]):
            return self._long_reply(self.jokes, 1, 2) if long else random.choice(self.jokes)

        # FACTS
        if self._matches(text, ["fact", "tell me something"]):
            return self._long_reply(self.facts, 1, 2) if long else random.choice(self.facts)

        # VIBE / MUSIC
        if any(x in text for x in ["vibe", "mood", "song", "music", "playlist"]):
            self.last_topic = "vibe"
            return self._long_reply(self.vibes, 1, 2)

        # PROBLEM SOLVING
        if any(x in text for x in ["problem", "help", "fix", "issue"]):
            self.last_topic = "problem"
            parts = [
                "Alright. Tell me what’s going on. Let’s fix it together.",
                "Start with the simplest description — what did you expect to happen?",
                "We’ll take it step by step, no rush."
            ]
            return self._long_reply(parts) if long else random.choice(parts)

        # CONTEXT FOLLOW-UP
        if self.last_topic == "feelings":
            return "I’m listening. You don’t have to rush. Say what you feel."

        if self.last_topic == "problem":
            return "Okay. Walk me through it step by step — what happened first?"

        # EXIT
        if any(x in text for x in ["bye", "exit", "stop", "goodbye"]):
            return "Alright. Take care — hit me up whenever."

        # SMALL TALK / COMPLIMENTS
        if any(x in text for x in ["cool", "nice", "love", "like", "dope"]):
            parts = [
                "That’s dope.",
                "Love hearing that.",
                "Nice — tell me more." 
            ]
            return self._long_reply(parts) if long else random.choice(parts)

        # HANDLE SHORT/AMBIGUOUS MESSAGES (encourage longer dialogue)
        if len(text.strip().split()) <= 3:
            prompts = [
                "Say more — what’s on your mind?",
                "I’m curious. Can you expand on that?",
                "Give me the vibe: funny, deep, or random?"
            ]
            return random.choice(prompts)

        # DEFAULT
        # sometimes produce a longer, vibey reply
        if long or random.random() < 0.25:
            return self._long_reply(self.default_lines + self.facts + self.vibes, 2, 3)

        return random.choice(self.default_lines)
