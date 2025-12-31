import random
import re

class NikBrain:
    def __init__(self):
        self.last_topic = None
        self.user_name = None
        self.conversation_depth = 0

        # --- CORE TOPIC KNOWLEDGE ---
        # Keeping these as they contain the specific information you requested
        self.topic_data = {
            'cars': [
                "The engineering in a modern supercar is lowkey mind-blowing.",
                "I'm a fan of classic muscle cars—they just had a different soul back then.",
                "EVs are the future for sure, but I'll miss the sound of a turbo spooling up.",
                "Aerodynamics is basically magic. How a car stays glued to the road at 200mph is wild.",
                "The shift toward autonomous driving is gonna change how cities are built."
            ],
            'ships': [
                "The sheer scale of an aircraft carrier is hard to wrap your head around.",
                "Sailing is the ultimate vibe—just you, the wind, and the horizon.",
                "Container ships are the literal backbone of the world. No ships, no tech.",
                "Deep-sea exploration is the final frontier. We know more about space than our own oceans.",
                "Ghost ships like the Mary Celeste are the ultimate maritime mystery."
            ],
            'geography': [
                "Geography dictates history. Mountains and rivers decide where empires start and end.",
                "The fact that there are uncontacted tribes in the Amazon in 2025 is fascinating.",
                "Iceland is basically another planet. Volcanoes and glaciers in the same spot.",
                "The Sahara Desert used to be a lush green forest. Earth's cycles are massive.",
                "I love how different time zones make it feel like we're living in different worlds."
            ],
            'philosophy': [
                "Stoicism is lowkey the best way to handle modern stress. Control what you can.",
                "The 'Ship of Theseus' thought experiment is a trip. If you replace every part, is it still the same?",
                "Existentialism isn't about being sad; it's about the freedom to choose your own path.",
                "Simulation theory is scary because it actually makes a lot of mathematical sense.",
                "Nietzsche's 'Eternal Recurrence' makes you think: would you live this exact life again forever?"
            ],
            'technology': [
                "AI is the biggest shift since the internet. It's moving at light speed rn.",
                "Quantum computing is gonna make our current supercomputers look like calculators.",
                "Neuralink and brain-computer interfaces are the next step. A bit sus, but cool.",
                "The amount of data we generate every day is literally exponential.",
                "Solid-state batteries are the holy grail for tech right now. Faster charging."
            ],
            'politics': [
                "Politics is basically just one big game of influence and optics.",
                "It's interesting how social media changed the way leaders communicate—for better or worse.",
                "The concept of a 'Global Village' is getting tested right now with all the border tension.",
                "Geopolitics is like a 4D chess game where the rules change every week.",
                "I try to stay out of the noise and just look at the long-term trends."
            ],
            'food': [
                "Cooking is the perfect mix of chemistry and art. Plus, you get to eat.",
                "Street food is usually better than fine dining. It's got more heart.",
                "The spice trade literally built the modern world. People used to go to war over pepper.",
                "Fermentation is wild—how bacteria can make food taste better and last longer.",
                "I'm lowkey convinced that pizza is the most universally loved thing on the planet."
            ],
            'clothes': [
                "Fashion is a language. What you wear says a lot before you even speak.",
                "Streetwear culture is basically the new high fashion.",
                "The 'fast fashion' cycle is crazy—clothes going from design to shelf in two weeks.",
                "Sustainable fabrics like hemp and recycled ocean plastic are the move.",
                "Thrifting is a top-tier vibe. Finding a 1-of-1 vintage piece hits different."
            ]
        }

        self.greetings = [

            "Yo. What's good?",

            "Hey hey — what's the vibe?",

            "What's up? I'm here.",

            "Ay, talk to me.",

            "Hey. How you feeling today?",

            "Yo yo. What's on your mind?",

            "Sup. Chill vibes only.",

            "What's happening? I'm all ears.",

            "Ayo, good to see you.",

            "Hey there. What brings you here?",

            "Wassup, ready to vibe?",

            "Greetings, friend. Let's chat."

        ]


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

            "I speak fluent sarcasm and broken code."

        ]


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

            "Some cats are allergic to humans. Plot twist."

        ]


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

            "What frequency are you on right now?"

        ]


        self.default_lines = [

            "Yeah, I feel you.",

            "Lowkey makes sense.",

            "Ngl, that's real.",

            "Hmm… interesting.",

            "I hear you.",

            "Go on, I'm listening.",

            "That's valid.",

            "Not gonna lie, that hits.",

            "Okay okay, I see where you're going.",

            "That's one way to look at it.",

            "Tell me more about that.",

            "I'm tracking with you.",

            "That resonates, honestly.",

            "Fair point right there.",

            "You're onto something.",

            "I respect that perspective.",

            "Keep going, this is good.",

            "Alright, I'm intrigued."

        ]


        self.reactions = [

            "Fr.",

            "Facts.",

            "Honestly?",

            "Real talk.",

            "No cap.",

            "For sure.",

            "Straight up.",

            "True that.",

            "100%.",

            "Absolutely.",

            "You ain't wrong.",

            "Big facts."

        ]


        self.slang = [

            "lowkey", "highkey", "vibe", "chill", "dope", "lit", "bet", "bruh", "fam",

            "ya", "yeah", "ngl", "no cap", "fr", "imo", "irl", "tbh", "tho", "rn",

            "sus", "slay", "valid", "mood", "same", "facts", "period", "tea"

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

            "Aight.",

            "Solid.",

            "Respect.",

            "Word.",

            "True.",

            "Copy that."

        ]


        self.chill_phrases = [

            "That's vibes.",

            "Super chill.",

            "We vibin'.",

            "All good here.",

            "Easy breezy.",

            "Keep it mellow.",

            "No stress zone.",

            "Peaceful energy only.",

            "Smooth sailing.",

            "Taking it easy."

        ]


        # Expanded emotional support responses

        self.emotional_support = {

            'sad': [

                "Damn… that sounds heavy.",

                "You don't gotta carry it alone.",

                "If you wanna vent, I'm here.",

                "Or we can switch vibes if that helps.",

                "It's okay to not be okay sometimes.",

                "Take all the time you need.",

                "Your feelings are valid, always.",

                "Want to talk about it or need a distraction?",

                "I'm not going anywhere. We can work through this.",

                "Some days are just harder. That's life, and that's real."

            ],

            'stressed': [

                "Stress hits different. What's weighing on you?",

                "Let's break it down piece by piece.",

                "Deep breath. You got this.",

                "Sometimes we just need to unload. I'm listening.",

                "What's the biggest thing stressing you out right now?",

                "Stress is temporary, but your strength is permanent.",

                "Let's tackle this together, no rush.",

                "You're doing more than you think. Give yourself credit."

            ],

            'excited': [

                "Yo, I can feel that energy! What's up?",

                "Let's gooo! Tell me everything.",

                "That's what I'm talking about!",

                "Hyped for you! What happened?",

                "Love this energy. Keep it coming.",

                "Your excitement is contagious. Spill the tea!",

                "This is the vibe we need. What's good?"

            ],

            'confused': [

                "Let's untangle this together.",

                "Confusion is just clarity waiting to happen.",

                "What part has you stuck?",

                "Walk me through it, we'll figure it out.",

                "Sometimes stepping back helps. What do you know so far?",

                "No worries, let's break it down simply."

            ]

        }


        # Deep conversation starters

        self.deep_topics = [

            "What's something you've been thinking about lately?",

            "If you could change one thing about your day, what would it be?",

            "What makes you feel most alive?",

            "What's a goal you're working toward?",

            "What's been on your mind that you haven't told anyone?",

            "If you had no limitations, what would you be doing right now?",

            "What's something you're grateful for today?"

        ]


        # Advice and problem-solving

        self.problem_solving = [

            "Alright, let's break it down.",

            "Tell me what happened.",

            "We'll fix it step by step, no stress.",

            "First things first: what's the core issue?",

            "Let's identify what you can control here.",

            "What have you tried so far?",

            "What would the ideal solution look like for you?",

            "Let's think through this logically, no pressure.",

            "What's your gut telling you?",

            "Sometimes the answer is simpler than we think."

        ]


        # Encouragement

        self.encouragement = [

            "You're stronger than you think.",

            "Every step forward counts, even the small ones.",

            "Progress isn't always visible, but it's there.",

            "You've got this. I believe in you.",

            "Keep going. You're on the right path.",

            "It's okay to rest, but don't quit.",

            "Your effort matters more than you know.",

            "Small wins are still wins. Celebrate them."

        ]


        self.typo_map = {

            "hello": ["helo", "helloo", "hallo"],

            "hello2": ["hi", "hey", "yo", "sup", "heya", "hiya"],

            "how are you": ["how r u", "how ru", "hru", "how ya doing", "how you been"],

            "sorry": ["sry", "mb", "my bad"],

            "i am": ["im", "i'm", "iam"],

            "thank": ["thx", "thanks", "ty", "tysm"]

        }

    def _clean(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s'?.!,]", " ", text)
        return re.sub(r'\s+', ' ', text)

    def _apply_style(self, resp, style):
        if not resp: return resp
        if style in ('chill', 'vibe') and random.random() < 0.35:
            token = random.choice(self.slang)
            resp = f"{token}, {resp}" if random.random() < 0.5 else f"{resp} — {token}"
        return resp

    def _matches(self, text, keywords):
        return any(k in text for k in keywords)

    def reply(self, text, long=False, style='chill'):
        text = self._clean(text)
        self.conversation_depth += 1

        topic_map = {
            'cars': ['car', 'auto', 'engine', 'tesla', 'driving', 'vehicle'],
            'ships': ['ship', 'boat', 'ocean', 'sailing', 'maritime', 'navy'],
            'geography': ['map', 'country', 'world', 'earth', 'mountain', 'city'],
            'philosophy': ['think', 'logic', 'meaning', 'exist', 'philosophy'],
            'technology': ['tech', 'computer', 'ai', 'software', 'robot', 'future'],
            'politics': ['politics', 'government', 'election', 'law', 'leader'],
            'food': ['food', 'eat', 'pizza', 'cooking', 'hungry', 'restaurant'],
            'clothes': ['clothes', 'fashion', 'outfit', 'style', 'wear', 'shoes']
        }

        for topic, keywords in topic_map.items():
            if self._matches(text, keywords):
                self.last_topic = topic
                responses = self.topic_data[topic]
                resp = random.choice(responses)
                
                if long and len(responses) > 1:
                    pair = random.sample(responses, 2)
                    resp = f"{pair[0]} {pair[1]}"
                
                return self._apply_style(resp, style)

        # Minimalist fallback since greetings/fillers were deleted
        return self._apply_style("I'm listening. Tell me more about that.", style)

    def reset_conversation(self):
        self.last_topic = None
        self.conversation_depth = 0