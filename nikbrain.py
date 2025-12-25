mport random

class NikBrain:
    def __init__(self):
        pass

    def reply(self, text):
        text = text.lower()

        if "hello" in text or "hi" in text:
            return "Hey. What’s up?"

        if "how are you" in text:
            return "I’m good. Chillin. You?"

        if "sad" in text:
            return "That sucks. Wanna talk about it?"

        if "bye" in text:
            return "Alright. Take it easy."

        replies = [
            "Yeah, I get that.",
            "Makes sense.",
            "Hmm… tell me more.",
            "I feel you."
        ]
        return random.choice(replies)