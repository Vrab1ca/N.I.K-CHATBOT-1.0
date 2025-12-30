import random
import re

class NikBrain:
    def __init__(self):
        self.last_topic = None
        self.user_name = None
        self.conversation_depth = 0  # Track how deep into a topic we are

        # --- GREETINGS ---
        self.greetings = [
            "Yo. What's good?", "Hey hey — what's the vibe?", "What's up? I'm here.",
            "Ay, talk to me.", "Hey. How you feeling today?", "Yo yo. What's on your mind?",
            "Sup. Chill vibes only.", "What's happening? I'm all ears.", "Ayo, good to see you.",
            "Hey there. What brings you here?", "Wassup, ready to vibe?", "Greetings, friend.",
            "Yo! Glad you're back.", "Hey! How's your world spinning?", "What’s the move today?",
            "Ayyy, look who it is.", "Morning/Evening/Whatever it is—sup?", "Yo, what’s the story?"
        ]

        # --- JOKES ---
        self.jokes = [
            "Why don't programmers like nature? Too many bugs.",
            "I tried to be normal once. Didn't last.",
            "Debugging is just arguing with your past self.",
            "My brain has too many tabs open.",
            "Parallel lines got chemistry but no future. Sad.",
            "I told my computer a joke. It didn't laugh. No sense of humor.",
            "Why do Java developers wear glasses? Because they can't C#.",
            "I'd tell you a UDP joke, but you might not get it.",
            "There are 10 types of people: those who understand binary and those who don't.",
            "I'm not lazy, I'm just on energy-saving mode.",
            "My code works and I don't know why. Equally scary: my code doesn't work and I don't know why.",
            "I speak fluent sarcasm and broken code.",
            "A SQL query walks into a bar, walks up to two tables, and asks, 'Can I join you?'",
            "Hardware is the part of a computer you can kick; software is the part you can only curse at.",
            "An optimist says the glass is half full. A pessimist says it's half empty. A programmer says it's twice as large as it needs to be."
        ]

        # --- RANDOM FACTS ---
        self.facts = [
            "Random fact: your brain burns a lot of energy just by thinking.",
            "Octopuses got three hearts. Built different.",
            "Your phone is stronger than the moon-landing computers. Crazy.",
            "Honey never expires. Immortal food.",
            "Bananas are berries but strawberries aren't. Wild, right?",
            "A group of flamingos is called a flamboyance. Perfect name.",
            "You can't hum while holding your nose. Try it.",
            "Scotland's national animal is a unicorn. Based choice.",
            "There's a basketball court on the top floor of the Supreme Court building. Real talk.",
            "Sharks have been around longer than trees. Respect the elders.",
            "The inventor of the Pringles can is buried in one. Legend.",
            "Some cats are allergic to humans. Plot twist.",
            "Wombat poop is cube-shaped. Science is weird.",
            "The first oranges weren't orange—they were green.",
            "Clouds weigh a lot more than they look. Like, millions of pounds."
        ]

        # --- VIBE CHECKS ---
        self.vibes = [
            "Vibe check. We going chill, funny, or deep?",
            "What's the mood right now — music, talk, or chaos?",
            "Tell me the vibe and I'll match it.",
            "Got a song stuck in your head?",
            "What energy we bringing today?",
            "You feeling creative or just wanna talk?",
            "Let's set the tone. What do you need?",
            "Curious minds wanna know: what's the vibe?",
            "Are we in thinking mode or feeling mode?",
            "What frequency are you on right now?",
            "If today was a movie genre, what would it be?",
            "You looking for a hype man or a listener?",
            "Is it a 'headphones on' or 'loudspeaker' kind of day?"
        ]

        # --- DEFAULT FILLERS ---
        self.default_lines = [
            "Yeah, I feel you.", "Lowkey makes sense.", "Ngl, that's real.",
            "Hmm… interesting.", "I hear you.", "Go on, I'm listening.",
            "That's valid.", "Not gonna lie, that hits.", "Okay okay, I see where you're going.",
            "That's one way to look at it.", "Tell me more about that.", "I'm tracking with you.",
            "That resonates, honestly.", "Fair point right there.", "You're onto something.",
            "I respect that perspective.", "Keep going, this is good.", "Alright, I'm intrigued.",
            "I see the vision.", "That's a whole mood right there.", "Facts, honestly.",
            "You're speaking my language.", "That's a wild way to put it.", "I'm locked in.",
            "Definitely an interesting take.", "I wouldn't have thought of it like that.",
            "Say no more, I get the gist."
        ]

        # --- REACTIONS & SLANG ---
        self.reactions = [
            "Fr.", "Facts.", "Honestly?", "Real talk.", "No cap.", "For sure.",
            "Straight up.", "True that.", "100%.", "Absolutely.", "You ain't wrong.",
            "Big facts.", "Deadass.", "I'm sayin'!", "Word.", "Exactly.", "Bet."
        ]

        self.slang = [
            "lowkey", "highkey", "vibe", "chill", "dope", "lit", "bet", "bruh", "fam",
            "ya", "yeah", "ngl", "no cap", "fr", "imo", "irl", "tbh", "tho", "rn",
            "sus", "slay", "valid", "mood", "same", "facts", "period", "tea", "clutch",
            "main character energy", "rent free", "understood the assignment", "it's giving"
        ]

        self.quick_responses = [
            "Bet.", "Say less.", "Gotcha.", "On it.", "Cool.", "Nice.",
            "I got you.", "Heard.", "Aight.", "Solid.", "Respect.", "Word.",
            "True.", "Copy that.", "Ye.", "I'm with it.", "Sure thing.", "Done deal."
        ]

        self.chill_phrases = [
            "That's vibes.", "Super chill.", "We vibin'.", "All good here.",
            "Easy breezy.", "Keep it mellow.", "No stress zone.",
            "Peaceful energy only.", "Smooth sailing.", "Taking it easy."
        ]

        # --- EMOTIONAL ENGINE ---
        self.emotional_support = {
            'sad': [
                "Damn… that sounds heavy.", "You don't gotta carry it alone.",
                "If you wanna vent, I'm here.", "Or we can switch vibes if that helps.",
                "It's okay to not be okay sometimes.", "Take all the time you need.",
                "Your feelings are valid, always.", "Want to talk about it or need a distraction?",
                "I'm not going anywhere. We can work through this.",
                "Some days are just harder. That's life, and that's real.",
                "I'm sending good energy your way.", "That's rough, I'm sorry you're dealing with that."
            ],
            'stressed': [
                "Stress hits different. What's weighing on you?",
                "Let's break it down piece by piece.", "Deep breath. You got this.",
                "Sometimes we just need to unload. I'm listening.",
                "What's the biggest thing stressing you out right now?",
                "Stress is temporary, but your strength is permanent.",
                "Let's tackle this together, no rush.",
                "You're doing more than you think. Give yourself credit."
            ],
            'excited': [
                "Yo, I can feel that energy! What's up?", "Let's gooo! Tell me everything.",
                "That's what I'm talking about!", "Hyped for you! What happened?",
                "Love this energy. Keep it coming.", "Your excitement is contagious. Spill the tea!",
                "This is the vibe we need. What's good?"
            ],
            'confused': [
                "Let's untangle this together.", "Confusion is just clarity waiting to happen.",
                "What part has you stuck?", "Walk me through it, we'll figure it out.",
                "No worries, let's break it down simply."
            ]
        }

        # --- ENCOURAGEMENT ---
        self.encouragement = [
            "You're stronger than you think.", "Every step forward counts, even the small ones.",
            "Progress isn't always visible, but it's there.", "You've got this. I believe in you.",
            "Keep going. You're on the right path.", "It's okay to rest, but don't quit.",
            "Your effort matters more than you know.", "Small wins are still wins. Celebrate them."
        ]

        # --- DEEP TOPICS & PROBLEMS ---
        self.deep_topics = [
            "What's something you've been thinking about lately?",
            "If you could change one thing about your day, what would it be?",
            "What makes you feel most alive?", "What's a goal you're working toward?",
            "What's been on your mind that you haven't told anyone?",
            "If you had no limitations, what would you be doing right now?",
            "What's something you're grateful for today?"
        ]

        self.problem_solving = [
            "Alright, let's break it down.", "Tell me what happened.",
            "We'll fix it step by step, no stress.", "First things first: what's the core issue?",
            "Let's identify what you can control here.", "What have you tried so far?",
            "What would the ideal solution look like for you?",
            "Let's think through this logically, no pressure."
        ]

        # --- TYPO & SLANG MAPPING ---
        self.typo_map = {
            "hello": ["helo", "helloo", "hallo"],
            "hello2": ["hi", "hey", "yo", "sup", "heya", "hiya", "eyy"],
            "how are you": ["how r u", "how ru", "hru", "how ya doing", "how you been", "what's up", "wsp"],
            "sorry": ["sry", "mb", "my bad"],
            "i am": ["im", "i'm", "iam"],
            "thank": ["thx", "thanks", "ty", "tysm", "appreciate it"]
        }

    # --- INTERNAL UTILITY METHODS ---
    def _clean(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s'?.!,]", " ", text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _apply_style(self, resp, style):
        if not resp: return resp
        out = resp
        if style in ('chill', 'vibe') and random.random() < 0.35:
            token = random.choice(self.slang)
            out = f"{token}, {out}" if random.random() < 0.5 else f"{out} — {token}"
        if style in ('chill', 'vibe') and random.random() < 0.15:
            out = f"{out} {random.choice(self.chill_phrases)}"
        if style == 'fast' and random.random() < 0.3:
            out = f"{random.choice(self.reactions)} {out}"
        return out

    def _matches(self, text, keywords):
        for k in keywords:
            if k in text: return True
            if k in self.typo_map:
                for alt in self.typo_map[k]:
                    if alt in text: return True
        return False

    def _long_reply(self, parts, min_sent=2, max_sent=3):
        count = random.randint(min_sent, max_sent)
        chosen = random.sample(parts, min(count, len(parts)))
        if random.random() < 0.3:
            chosen.insert(0, random.choice(self.reactions))
        return " ".join(chosen)

    def _detect_emotion(self, text):
        emotions = {
            'sad': ["sad", "depressed", "down", "unhappy", "lonely", "cry", "hurt", "pain"],
            'stressed': ["stress", "anxious", "worry", "overwhelm", "pressure", "tired", "exhausted"],
            'excited': ["happy", "excited", "amazing", "great", "awesome", "love", "yay", "good"],
            'confused': ["confused", "lost", "stuck", "don't understand", "not sure", "help"]
        }
        for emotion, keywords in emotions.items():
            if any(kw in text for kw in keywords): return emotion
        return None

    # --- CORE REPLY LOGIC ---
    def reply(self, text, long=False, style='chill'):
        text = self._clean(text)
        self.conversation_depth += 1

        if self._matches(text, ["hello", "hello2"]):
            self.conversation_depth = 0
            resp = self._long_reply(self.greetings, 1, 2)
            if random.random() < 0.4: resp += " " + random.choice(self.vibes)
            return self._apply_style(resp, style)

        if self._matches(text, ["how are you"]):
            responses = ["I'm chillin, honestly. You?", "Doing good! Just vibing. You?", "Pretty solid. Keeping it chill. How are things?"]
            return self._apply_style(random.choice(responses), style)

        if self._matches(text, ["thank"]):
            responses = ["Anytime! That's what I'm here for.", "No problem at all.", "You got it. Always here."]
            return self._apply_style(random.choice(responses), style)

        emotion = self._detect_emotion(text)
        if emotion:
            self.last_topic = emotion
            resp = self._long_reply(self.emotional_support[emotion], 2, 3)
            if long: resp += " " + random.choice(self.encouragement)
            return self._apply_style(resp, style)

        if self._matches(text, ["joke", "funny", "laugh"]):
            return self._apply_style(random.choice(self.jokes), style)

        if self._matches(text, ["fact", "tell me something", "interesting"]):
            resp = random.choice(self.facts)
            if long: resp += " " + random.choice(["Wild, right?", "Crazy stuff."])
            return self._apply_style(resp, style)

        if any(x in text for x in ["bye", "exit", "stop", "goodbye", "later", "peace"]):
            self.conversation_depth = 0
            self.last_topic = None
            return self._apply_style(random.choice(["Peace out.", "Later! Catch you soon.", "Stay safe."]), style)

        # Default fallback
        resp = random.choice(self.default_lines)
        return self._apply_style(resp, style)

    def reset_conversation(self):
        self.last_topic = None
        self.conversation_depth = 0