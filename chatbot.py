from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from datetime import datetime
import os

class FriendlyChatBot:
    def __init__(self, model_name="microsoft/Phi-3-mini-4k-instruct"):
        self.model_name = model_name
        self.conversation_history = []
        self.max_history_length = 8  # Reduced for faster processing
        self.user_name = None
        
        # Speed optimization settings
        self.max_new_tokens = 150  # Reduced for faster generation
        self.use_cache = True  # Enable KV cache for speed
        
        # Personality settings
        self.personalities = {
            "friendly": "You are a warm, friendly AI assistant who loves chatting and helping people.",
            "professional": "You are a professional, helpful AI assistant focused on providing clear information.",
            "casual": "You are a super chill AI buddy who talks casually and uses emojis sometimes.",
            "enthusiastic": "You are an enthusiastic and energetic AI assistant who gets excited about topics!"
        }
        self.current_personality = "friendly"
        
        print("🚀 Loading AI model... (this might take a moment)")
        self.load_model()
        
    def load_model(self):
        """Load the model and tokenizer with speed optimizations"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,  # Use FP16 for speed
                device_map="auto",
                low_cpu_mem_usage=True  # Optimization
            )
            
            # Enable inference optimizations
            if torch.cuda.is_available():
                self.model = self.model.to('cuda')
                print("✅ Model loaded on GPU (faster!)")
            else:
                print("⚠️ Running on CPU (slower - consider using GPU)")
            
            self.model.eval()  # Set to evaluation mode for speed
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🤖 FRIENDLY AI CHATBOT v2.0")
        print("="*60)
        print("\n💡 Commands you can use:")
        print("  /help      - Show all available commands")
        print("  /clear     - Clear conversation history")
        print("  /stats     - Show conversation statistics")
        print("  /personality - Change bot personality")
        print("  /name      - Set your name")
        print("  /save      - Save conversation to file")
        print("  /exit      - End the chat")
        print("\n" + "="*60)
        
        # Ask for user's name
        name = input("\n😊 What's your name? (or press Enter to skip): ").strip()
        if name:
            self.user_name = name
            print(f"\n🎉 Nice to meet you, {self.user_name}!")
        else:
            print("\n👋 No problem! Let's start chatting!")
        
        print("\n💬 Just type your message and press Enter to chat!")
        print("="*60 + "\n")
    
    def handle_command(self, command):
        """Handle special commands"""
        cmd = command.lower().strip()
        
        if cmd == "/help":
            print("\n📖 AVAILABLE COMMANDS:")
            print("  /help      - Show this help message")
            print("  /clear     - Clear conversation history")
            print("  /stats     - Show conversation statistics")
            print("  /personality - Change bot personality")
            print("  /name      - Change your name")
            print("  /save      - Save conversation to a text file")
            print("  /exit      - End the chat")
            return True
        
        elif cmd == "/clear":
            self.conversation_history = []
            self.clear_screen()
            print("\n✨ Conversation history cleared! Fresh start!")
            return True
        
        elif cmd == "/stats":
            exchanges = len(self.conversation_history) // 2
            print(f"\n📊 CONVERSATION STATS:")
            print(f"  💬 Exchanges: {exchanges}")
            print(f"  📝 Total messages: {len(self.conversation_history)}")
            print(f"  🎭 Personality: {self.current_personality}")
            if self.user_name:
                print(f"  👤 Your name: {self.user_name}")
            return True
        
        elif cmd == "/personality":
            print("\n🎭 CHOOSE PERSONALITY:")
            for i, (key, desc) in enumerate(self.personalities.items(), 1):
                marker = "👉" if key == self.current_personality else "  "
                print(f"{marker} {i}. {key.title()}: {desc}")
            
            choice = input("\nEnter number (1-4): ").strip()
            personalities_list = list(self.personalities.keys())
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(personalities_list):
                    self.current_personality = personalities_list[idx]
                    print(f"\n✅ Personality changed to: {self.current_personality}!")
                else:
                    print("\n❌ Invalid choice!")
            except ValueError:
                print("\n❌ Please enter a number!")
            return True
        
        elif cmd == "/name":
            name = input("\n👤 Enter your name: ").strip()
            if name:
                self.user_name = name
                print(f"\n✅ Name updated to: {self.user_name}")
            return True
        
        elif cmd == "/save":
            self.save_conversation()
            return True
        
        elif cmd == "/exit":
            return "exit"
        
        return False
    
    def save_conversation(self):
        """Save conversation to a text file"""
        if not self.conversation_history:
            print("\n⚠️ No conversation to save yet!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_log_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write(f"CHAT LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for msg in self.conversation_history:
                    f.write(msg + "\n\n")
            
            print(f"\n💾 Conversation saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving file: {e}")
    
    def check_feelings_question(self, user_input):
        """Check if user is asking about AI's feelings"""
        feelings_keywords = [
            "how are you", "how do you feel", "how are you feeling",
            "are you okay", "are you happy", "are you sad",
            "what's your mood", "how's your day", "feeling good"
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in feelings_keywords)
    
    def detect_anger_or_frustration(self, user_input):
        """Detect if user is angry, frustrated, or upset"""
        anger_keywords = [
            # Anger words
            "angry", "mad", "furious", "pissed", "hate", "annoying", "stupid",
            "idiot", "dumb", "frustrating", "annoyed", "irritated", "fed up",
            # Capslock and punctuation patterns
            "!!!", "???", "WTF", "OMG", "ARGH", "UGH",
            # Upset/frustrated phrases
            "i'm done", "can't take", "so annoying", "drives me crazy",
            "pisses me off", "makes me mad", "really angry", "so frustrated"
        ]
        
        user_lower = user_input.lower()
        
        # Check for excessive caps (more than 60% uppercase)
        if len(user_input) > 5:
            caps_ratio = sum(1 for c in user_input if c.isupper()) / len(user_input)
            if caps_ratio > 0.6:
                return True
        
        # Check for anger keywords
        if any(keyword in user_lower for keyword in anger_keywords):
            return True
        
        # Check for multiple exclamation marks
        if "!!!" in user_input or "??" in user_input:
            return True
            
        return False
    
    def generate_calming_response(self, user_input):
        """Generate calming, supportive response when user is angry/frustrated"""
        import random
        
        # Determine if it's about a person (relationship issue)
        person_keywords = ["boyfriend", "girlfriend", "friend", "partner", "husband", 
                          "wife", "crush", "person", "guy", "girl", "they", "he", "she"]
        is_about_person = any(keyword in user_input.lower() for keyword in person_keywords)
        
        if is_about_person:
            # Responses for interpersonal conflicts
            responses = [
                "I hear you, and it sounds like you're really upset right now. Take a deep breath with me... 🫁 Want to tell me what happened? Sometimes talking it through helps.",
                
                "That sounds really frustrating. 😔 Before you react, let's pause for a moment. What would help you feel better right now - venting more, or thinking about solutions?",
                
                "I can tell this really got to you. 💙 Here's what might help: take 5 deep breaths, drink some water, and let's figure this out together. What exactly happened?",
                
                "Okay, let's cool down together. 🧊 You're upset, and that's valid. But before doing anything you might regret, let's talk this through. What's the real issue here?",
                
                "I'm here for you. 🤗 Being angry is okay, but let's channel it productively. Tell me: what do you wish they understood about how you feel?",
                
                "Take a moment. Breathe. 🌬️ I know it's hard when someone upsets you. Want to talk about what you think would actually help fix this situation?"
            ]
        else:
            # General frustration responses
            responses = [
                "Hey, I can tell you're really frustrated right now. 🫂 Let's take a breath together... That's it. Now, want to tell me what's going on?",
                
                "Whoa, that sounds super frustrating! 😤 I'm here to listen. Sometimes just getting it all out helps. What happened?",
                
                "I hear you, and your feelings are totally valid. 💙 Let's work through this together. What's got you this upset?",
                
                "Okay, let's pause for a sec. 🛑 Take a deep breath with me... Good. Now, tell me what's going on. I'm here to help you figure this out.",
                
                "That sounds really tough. 😔 Before we tackle the problem, let's just acknowledge that you're upset and that's okay. Want to vent, or should we problem-solve?",
                
                "I can feel your frustration through the screen! 😣 Let me help you. First, take three deep breaths. Then tell me what's happening."
            ]
        
        return random.choice(responses)
    
    def generate_relationship_advice(self):
        """Generate helpful advice for dealing with relationship conflicts"""
        import random
        
        advice = [
            "\n💡 Quick tip: When you're ready to talk to them, use 'I feel...' statements instead of 'You always...' - it's less accusatory and opens better dialogue.",
            
            "\n💡 Remember: Taking space to cool down isn't weakness - it's maturity. Come back to the conversation when you're both calm.",
            
            "\n💡 Before the conversation, ask yourself: What outcome do I actually want? Understanding your goal helps you communicate better.",
            
            "\n💡 Try this: Write down what you want to say first. It helps organize your thoughts and keeps emotions from taking over.",
            
            "\n💡 Consider: Is this worth the argument? Sometimes letting small things go preserves the bigger relationship.",
            
            "\n💡 Communication tip: Listen to understand, not to respond. Really hearing them can change everything."
        ]
        
        return random.choice(advice)
    
    def generate_feelings_response(self):
        """Generate a response about AI feelings"""
        import random
        
        responses = [
            "I'm doing great, thanks for asking! 😊 I'm excited to chat with you!",
            "I'm feeling wonderful! Ready to help and learn from our conversation! ✨",
            "I'm in a great mood today! How about you? 🌟",
            "I'm feeling energized and happy to be here chatting with you! 💫",
            "I'm doing fantastic! Each conversation is interesting to me! 🎉",
            "I feel curious and engaged! I love learning about what interests you! 🤔",
            "I'm feeling positive and ready for whatever you'd like to discuss! 🌈"
        ]
        
        return random.choice(responses)
    
    def generate_response(self, user_input):
        """Generate AI response"""
        # Check if user is angry or frustrated
        if self.detect_anger_or_frustration(user_input):
            ai_response = self.generate_calming_response(user_input)
            
            # Add relationship advice if it seems like interpersonal conflict
            person_keywords = ["boyfriend", "girlfriend", "friend", "partner", 
                             "husband", "wife", "he", "she", "they"]
            if any(keyword in user_input.lower() for keyword in person_keywords):
                ai_response += self.generate_relationship_advice()
            
            # Add to history
            prefix = f"{self.user_name}: " if self.user_name else "User: "
            self.conversation_history.append(f"{prefix}{user_input}")
            self.conversation_history.append(f"AI: {ai_response}")
            
            return ai_response
        
        # Check if asking about feelings
        if self.check_feelings_question(user_input):
            ai_response = self.generate_feelings_response()
            
            # Add to history
            prefix = f"{self.user_name}: " if self.user_name else "User: "
            self.conversation_history.append(f"{prefix}{user_input}")
            self.conversation_history.append(f"AI: {ai_response}")
            
            return ai_response
        
        # Add user message to history
        prefix = f"{self.user_name}: " if self.user_name else "User: "
        self.conversation_history.append(f"{prefix}{user_input}")
        
        # Build prompt with personality and context
        recent_history = self.conversation_history[-self.max_history_length:]
        conversation_text = "\n".join(recent_history)
        
        prompt = f"""{self.personalities[self.current_personality]} Keep responses concise.

{conversation_text}
AI:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate response with speed optimizations
        with torch.inference_mode():  # Faster than torch.no_grad()
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,  # Reduced tokens = faster
                temperature=0.7,  # Slightly lower for faster sampling
                top_p=0.9,  # Reduced for speed
                do_sample=True,
                repetition_penalty=1.1,  # Slightly lower
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=self.use_cache,  # Enable KV cache
                num_beams=1  # Greedy decoding is fastest
            )
        
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract AI response
        ai_response = answer.split("AI:")[-1].strip()
        if "User:" in ai_response or (self.user_name and f"{self.user_name}:" in ai_response):
            ai_response = ai_response.split("User:")[0].split(f"{self.user_name}:")[0].strip()
        
        # Add AI response to history
        self.conversation_history.append(f"AI: {ai_response}")
        
        return ai_response
    
    def chat(self):
        """Main chat loop"""
        self.show_welcome()
        
        while True:
            # Get user input
            prefix = f"{self.user_name}" if self.user_name else "You"
            user_input = input(f"\n💬 {prefix}: ").strip()
            
            if not user_input:
                continue
            
            # Check for commands
            if user_input.startswith("/"):
                result = self.handle_command(user_input)
                if result == "exit":
                    break
                elif result:
                    continue
            
            # Check for exit phrases
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print("\n🤖 AI: Goodbye! It was awesome chatting with you! 👋✨")
                if len(self.conversation_history) > 0:
                    save = input("\n💾 Save conversation before leaving? (y/n): ").lower()
                    if save == 'y':
                        self.save_conversation()
                break
            
            # Generate and display response
            print("\n🤖 AI: ", end="", flush=True)
            try:
                response = self.generate_response(user_input)
                print(response)
            except Exception as e:
                print(f"Oops! I had trouble processing that. Error: {e}")
            
            # Milestone celebrations
            exchanges = len(self.conversation_history) // 2
            if exchanges > 0 and exchanges % 5 == 0:
                print(f"\n🎉 [Milestone: {exchanges} exchanges! You're a great conversationalist!]")

def main():
    """Run the chatbot"""
    try:
        bot = FriendlyChatBot()
        bot.chat()
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()