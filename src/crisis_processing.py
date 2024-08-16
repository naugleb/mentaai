import logging
from telegram import Update
from telegram.ext import ContextTypes
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from resources import critical_keywords, dangerous_keywords

# Set up logging to capture information and errors for debugging
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer for detecting emotional tone in user messages
analyzer = SentimentIntensityAnalyzer()

# Function to detect crisis situations based on keywords and sentiment analysis
def detect_crisis(message):
    # Check for critical and dangerous keywords in the user's message
    contains_critical_keyword = any(keyword in message.lower() for keyword in critical_keywords)
    contains_dangerous_keyword = any(keyword in message.lower() for keyword in dangerous_keywords)
    # Analyze the sentiment score of the message
    sentiment_score = analyzer.polarity_scores(message)['compound']
    logger.info(f"Sentiment score: {sentiment_score} for message: {message[:30]}...")  # Anonymized logging
    # Trigger crisis response immediately if a critical keyword is found
    if contains_critical_keyword:
        return True
    # Trigger crisis response if a dangerous keyword is found and sentiment is below the threshold
    if contains_dangerous_keyword and sentiment_score <= -0.6:
        return True
    # Otherwise, do not trigger crisis response
    return False

# Asynchronous function to send a crisis response with UK-specific resources
async def crisis_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Immediate supportive response to a detected crisis situation
    crisis_message = (
        "It sounds like you're going through something very difficult right now, and I'm really sorry to hear that. "
        "Please know that there is help available. "
        "If you're in the UK, here are some important resources:\n\n"
        "1. Samaritans: Call 116 123 (24/7) - Samaritans is a confidential emotional support service, available 24/7 for anyone in distress, struggling to cope, or at risk of suicide.\n"
        "2. Shout: Text 'SHOUT' to 85258 - Shout is a free, confidential text messaging service available 24/7 for anyone in crisis, providing support for issues like suicidal thoughts, anxiety, depression, and more.\n"
        "3. NHS: Call 111 for non-emergency help - For non-urgent medical advice and support from the NHS.\n"
        "4. Emergency Services: Call 999 if you or someone else is in immediate danger.\n\n"
        "In the meantime, try focusing on your breathing: take deep, slow breaths. "
        "Grounding techniques can also help, such as touching something with texture or naming five things you can see around you. "
        "Remember, reaching out for help is a strong and positive step."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=crisis_message)