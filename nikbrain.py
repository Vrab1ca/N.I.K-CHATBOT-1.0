import random

class NikBrain:
    def __init__(self):
        self.last_topic = None

    def reply(self, text):
        text = text.lower()

        # -------- GREETINGS --------
        if any(x in text for x in ["hello", "hi", "hey"]):
            return random.choice([
                "Hey. What’s good?",
                "Yo. How you doing?",
                "Hey hey. Talk to me."
            ])

        # -------- FEELINGS --------
        if "how are you" in text:
            return "I’m chillin. Not gonna lie. How about you?"

        if any(x in text for x in ["sad", "depressed", "bad day"]):
            self.last_topic = "feelings"
            return "Damn… that’s rough. Wanna talk about it or distract yourself?"

        # -------- FUN / JOKES --------
        if any(x in text for x in ["joke", "funny"]):
            return random.choice([
                "Why don’t programmers like nature? Too many bugs.",
                "I tried to be normal once. Worst two minutes of my life.",
                "Debugging is like being a detective in your own crime movie."
            ])

        # -------- FACTS --------
        if any(x in text for x in ["fact", "tell me something"]):
            return random.choice([
                "Fun fact. Your brain uses about twenty percent of your body’s energy.",
                "Octopuses have three hearts. Yeah. Wild.",
                "Your phone is more powerful than computers from the moon landing."
            ])

        # -------- PROBLEM SOLVING --------
        if any(x in text for x in ["problem", "help", "fix"]):
            self.last_topic = "problem"
            return "Alright. Tell me what’s going on. Let’s fix it."

        # -------- CONTEXT FOLLOW-UP --------
        if self.last_topic == "feelings":
            return "I’m listening. You don’t have to rush."

        if self.last_topic == "problem":
            return "Okay. Walk me through it step by step."

        # -------- EXIT --------
        if any(x in text for x in ["bye", "exit", "stop"]):
            return "Alright. Take care. Talk soon."

        # -------- DEFAULT CHAT --------
        return random.choice([
            "Yeah, I feel that.",
            "Makes sense honestly.",
            "Go on. I’m listening.",
            "Hmm. Interesting.",
            "Not gonna lie, that’s real."
        ])