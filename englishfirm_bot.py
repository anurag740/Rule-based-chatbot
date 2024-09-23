import re
import spacy
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define keyword patterns and responses
patterns = {
    "classes": re.compile(r"(class|course|types of classes|offer)"),
    "ielts": re.compile(r"(ielts|ielts coaching)"),
    "fees": re.compile(r"(fees|cost|price|fee)"),
    "schedule": re.compile(r"(schedule|next batch|time)"),
    "contact": re.compile(r"(contact|phone number|email)"),
    "online": re.compile(r"(online classes|remote|virtual)"),
    "location": re.compile(r"(where|location|branch)"),
    "instructor": re.compile(r"(instructor|teacher|trainer|certified)")
}


# Responses
responses = {
    "classes": "We offer IELTS, PTE, General English, and Business English classes. Englishfirm offers PTE, IELTS, NAATI, and General English coaching. They provide one-on-one sessions, and both online and in-person options in Sydney, Melbourne, and Kochi. There are two-week crash courses and unlimited practice sessions available for PTE. Classes can be booked through the website, with flexible timing options :  https://englishfirm.com/",
    "ielts": "Yes, we provide expert IELTS coaching with certified trainers to help you achieve your desired band score.",
    "fees": "The fees for IELTS coaching vary based on the course duration and mode of learning. You can book a free 30-minute demo session with access to mock tests and practice materials before committing to a paid course. Fees for extended courses vary depending on the duration and type (e.g., crash courses, unlimited classes), but specific pricing details should be confirmed via our contact numbers. Please contact us for detailed pricing information : https://englishfirm.com/",
    "schedule": "Our next IELTS batch starts on the 1st of the upcoming month. You can register online or call us for more details. Classes run seven days a week, with branches in Sydney and Melbourne, plus flexible online classes for remote students. You can also book classes year-round :  https://englishfirm.com/",
    "contact": "You can contact us at +61 2 8006 2063 or info@englishfirm.com for further inquiries.",
    "online": "Yes, we offer online classes so you can learn from the comfort of your home.",
    "location": "Englishfirm has centers across Australia, including Sydney and Melbourne. We have branches in Parramatta (Sydney), Melbourne, and Kochi, Kerala. Online classes are available for students in other parts of Australia and internationally. Check our website for the nearest location to you:  https://englishfirm.com/",
    "instructor": "Our instructors are experienced and certified IELTS and PTE trainers. Trainers at Englishfirm, such as Avanti and Vandana, are experienced in coaching for PTE and IELTS with personalized attention. They emphasize individual growth, mentoring students to help them achieve their language goals."
}

# Extended greeting and farewell responses
greeting_responses = [
    "Hello! How can I assist you today?",
    "Hi there! What can I help you with?",
    "Hey! How's it going?",
    "Good morning! How can I help you today?",
    "Good afternoon! What can I assist you with?"
]
farewell_responses = [
    "Goodbye! Have a great day!",
    "Bye! Feel free to reach out anytime.",
    "Take care!"
]
negative_response = ("no", "nope", "nah", "naw", "not a chance", "sorry")
exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later")

# Additional conversational responses for greetings
how_are_you_responses = [
    "I'm doing great! Thanks for asking.",
    "I'm just a bot, but I'm here to help you!",
    "I'm good! How about you?",
    "I'm always ready to assist you with any questions you have."
]
whats_up_responses = [
    "Not much, just here to help you out!",
    "Nothing much, what's up with you?",
    "I'm here to assist you with any queries you have."
]

context = None
user_name = None

def analyze_user_input(user_input):
    doc = nlp(user_input)
    tokens = [token.text.lower() for token in doc if not token.is_stop]
    return tokens

def check_greeting(user_input):
    greetings = ["hi", "hey", "hello", "howdy", "how are you", "good morning", "good afternoon", "good evening", "what's up"]
    for word in user_input.split():
        if word.lower() in greetings:
            return True
    return False

def handle_specific_greetings(user_input):
    if "how are you" in user_input.lower():
        return how_are_you_responses[0] if not user_name else f"I'm good, {user_name}! How about you?"
    elif "what's up" in user_input.lower():
        return whats_up_responses[0]
    return None

def extract_name(user_input):
    doc = nlp(user_input)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def chatbot_response(user_input):
    global context, user_name
    
    if any(command in user_input.lower() for command in exit_commands):
        return farewell_responses[0]

    specific_greeting_response = handle_specific_greetings(user_input)
    if specific_greeting_response:
        return specific_greeting_response

    if check_greeting(user_input):
        return f"{greeting_responses[0]} What can I help you with?" if not user_name else f"Hello again, {user_name}! How can I assist you?"
    
    name = extract_name(user_input)
    if name:
        user_name = name
        return f"Nice to meet you, {user_name}! How can I assist you today?"
    
    tokens = analyze_user_input(user_input)
    if context == "classes" and ("fees" in tokens or "cost" in tokens):
        return "The fees for IELTS coaching vary based on the course duration and mode of learning. You can book a free 30-minute demo session with access to mock tests and practice materials before committing to a paid course. Fees for extended courses vary depending on the duration and type (e.g., crash courses, unlimited classes), but specific pricing details should be confirmed via our contact numbers. Please contact us for detailed pricing information : https://englishfirm.com/"
    elif context == "classes" and ("schedule" in tokens or "time" in tokens):
        return "Our next IELTS batch starts on the 1st of the upcoming month."
    
    for token in tokens:
        for intent, pattern in patterns.items():
            if re.search(pattern, token):
                context = intent
                return responses[intent]
    
    context = None
    return "I'm sorry, I don't have the information you're looking for. I'm here to assist you with any queries you have."

async def start(update: Update, context):
    await update.message.reply_text("Welcome to Englishfirm chatbot! I'm here to assist you with any queries you have.")

async def handle_message(update: Update, context):
    user_input = update.message.text
    response = chatbot_response(user_input)
    await update.message.reply_text(response)

if __name__ == '__main__':
    # Replace 'YOUR_TOKEN_HERE' with your actual bot token
    application = Application.builder().token('Replace 'YOUR_TOKEN_HERE' with your actual bot token').build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()
