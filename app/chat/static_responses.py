"""
Static responses for simple conversational intents.

These responses bypass:
- embeddings
- ChromaDB
- retrieval
- Groq/LLM
"""


GREETING_RESPONSES = {

    # =========================================================
    # GREETINGS
    # =========================================================

    "hi": "Hi! How can I help you?",
    "hello": "Hello! How can I help you?",
    "hey": "Hey! How can I help you?",
    "hiya": "Hi! How can I help you?",

    "hi there": "Hi there! How can I help you?",
    "hello there": "Hello there! How can I help you?",
    "hey there": "Hey there! How can I help you?",

    "good morning": "Good morning! How can I help you today?",
    "good afternoon": "Good afternoon! How can I help you today?",
    "good evening": "Good evening! How can I help you today?",
    "good night": "Good night! Have a good rest.",

    "morning": "Good morning! How can I help you?",
    "afternoon": "Good afternoon! How can I help you?",
    "evening": "Good evening! How can I help you?",


    # =========================================================
    # HOW ARE YOU / WELLBEING
    # =========================================================

    "how are you": "I'm doing well, thank you. How can I help you?",
    "how are you doing": "I'm doing well, thank you. How can I help you?",
    "how are things": "Things are going well. How can I help you?",
    "how's it going": "It's going well. How can I help you?",
    "hows it going": "It's going well. How can I help you?",
    "how have you been": "I'm doing well, thank you. How can I help you?",
    "are you doing well": "Yes, I'm doing well. How can I help you?",
    "are you okay": "Yes, I'm ready to help. What would you like to know?",


    # =========================================================
    # COMPLIMENTS
    # =========================================================

    "you are nice": "Thank you! That's very kind of you.",
    "you're nice": "Thank you! That's very kind of you.",
    "you are very nice": "Thank you! That's very kind of you.",
    "you're very nice": "Thank you! That's very kind of you.",

    "you are helpful": "Thank you! I'm glad I could help.",
    "you're helpful": "Thank you! I'm glad I could help.",

    "you are great": "Thank you! I appreciate that.",
    "you're great": "Thank you! I appreciate that.",

    "you are amazing": "Thank you! I appreciate that.",
    "you're amazing": "Thank you! I appreciate that.",

    "you are awesome": "Thank you! That's very kind of you.",
    "you're awesome": "Thank you! That's very kind of you.",

    "good job": "Thank you! I'm glad I could help.",
    "well done": "Thank you! I'm glad I could help.",

    "nice": "Thank you! How can I help you?",
    "great": "Thank you! How can I help you?",


    # =========================================================
    # THANKS
    # =========================================================

    "thanks": "You're welcome!",
    "thank you": "You're welcome!",
    "thanks a lot": "You're welcome!",
    "thank you very much": "You're very welcome!",
    "many thanks": "You're welcome!",
    "thx": "You're welcome!",
    "ty": "You're welcome!",


    # =========================================================
    # GOODBYE
    # =========================================================

    "bye": "Goodbye! Have a great day.",
    "goodbye": "Goodbye! Have a great day.",
    "bye bye": "Goodbye! Have a great day.",
    "see you": "See you later!",
    "see you later": "See you later!",
    "talk to you later": "Sure. Talk to you later!",
    "take care": "Take care! Have a great day.",
    "have a good day": "Thank you! Have a good day too.",
    "have a nice day": "Thank you! Have a nice day too.",


    # =========================================================
    # INTRODUCTION / IDENTITY
    # =========================================================

    "who are you": (
        "I'm the AI Guidance Chatbot, an assistant for "
        "answering questions from the available knowledge base."
    ),

    "what are you": (
        "I'm the AI Guidance Chatbot. "
        "I can help answer questions using the available knowledge base."
    ),

    "what can you do": (
        "I can answer questions using the available internal knowledge."
    ),

    "what do you do": (
        "I help answer questions using the available internal knowledge."
    ),


    # =========================================================
    # HELP
    # =========================================================

    "help": "Sure. Ask me a question about the available internal documents.",
    "can you help me": "Of course. What would you like help with?",
    "i need help": "Sure. What can I help you with?",
    "help me": "Sure. What would you like help with?",


    # =========================================================
    # POLITENESS / ACKNOWLEDGEMENT
    # =========================================================

    "okay": "Sure. How can I help you?",
    "ok": "Sure. How can I help you?",
    "alright": "Alright. How can I help you?",
    "sounds good": "Great. How can I help you?",
    "got it": "Great. Let me know if you need anything else.",
    "understood": "Great. Let me know if you need anything else.",
    "perfect": "Great! How can I help you?",
}


def get_static_greeting(query: str) -> str | None:
    """
    Return a predefined response for a known greeting.

    Returns:
        str: Static response if the query is a known greeting.
        None: If the query is not a known greeting.
    """

    normalized_query = query.strip().lower()

    return GREETING_RESPONSES.get(normalized_query)