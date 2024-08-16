import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from crisis_processing import detect_crisis, crisis_response
from context_retrieval import retrieve_similar_transcripts_chain
from models_initialization import emotion_classifier, client_manager_system_message, llm
from proxy_setup import create_http_client_with_proxy
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory, ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging to capture information and errors for debugging
logger = logging.getLogger(__name__)

# Initialize user state to keep track of user-specific data
user_state = {}

# Initialize conversation memories with separate instances for each user
user_memories = {}

# Set up an HTTP client with proxy for summary memory
http_client_summary = create_http_client_with_proxy()

# Define a prompt template for generating responses using the language model chain
prompt_template = PromptTemplate(
    input_variables=["system_message", "retrieved_context", "memory_context", "user_name", "prompt", "emotion"],
    template="""
    Instructions:
    {system_message}
    User's name: {user_name}
    Memory Context:
    {memory_context}
    {retrieved_context}
    Client: {prompt}
    Detected Emotion: {emotion}
    Counselor:
    """
)

# Create a language model chain with the defined prompt template
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

# Initialize global conversation memory
def initialize_memory(user_id):
    if user_id not in user_memories:
        user_memories[user_id] = {
            'buffer_memory': ConversationBufferWindowMemory(k=3),
            'summary_memory': ConversationSummaryMemory(
                llm=ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model='gpt-4o', http_client=http_client_summary, temperature=0.3),
                return_messages=True
            )
        }

# Function to manage conversation memory and retrieve the user's name
def memory_chain(user_id):
    initialize_memory(user_id)
    # Retrieve conversation memory context
    buffer_memory = user_memories[user_id]['buffer_memory']
    summary_memory = user_memories[user_id]['summary_memory']
    try:
        buffer_context = buffer_memory.load_memory_variables({}).get('history', [])
        logger.info(f"Buffer context loaded for user {user_id}: {buffer_context}")
    except Exception as e:
        buffer_context = []
        logger.error(f"Error loading buffer memory for user {user_id}: {e}")
    
    try:
        summary_list = summary_memory.load_memory_variables({}).get('history', [])
        summary_context = "\n".join([msg.content for msg in summary_list]) if summary_list else ""
        logger.info(f"Summary context loaded for user {user_id}: {summary_context}")
    except Exception as e:
        summary_context = ""
        logger.error(f"Error loading summary memory for user {user_id}: {e}")

    # Combine buffer and summary contexts
    memory_context = f"Summary:\n{summary_context}\n\nRecent Interactions:\n{buffer_context}"
    # Retrieve the user's name from the state
    user_name = user_state.get(user_id, {}).get("name", "")
    
    return memory_context, user_name

# Function to generate a response based on user input, detected emotion, and retrieved context
def generate_response(prompt, user_id):
    try:
        # Retrieve conversation memory and user's name
        memory_context, user_name = memory_chain(user_id)
        # Retrieve similar transcripts to use as context
        retrieved_context = retrieve_similar_transcripts_chain(prompt)
        
        # Detect emotion in the user's input
        emotion_scores = emotion_classifier(prompt)
        emotion = max(emotion_scores[0], key=lambda x: x['score'])['label']

        # Build the full prompt for logging
        full_prompt = f"""
        {client_manager_system_message.content}
        User's name: {user_name}
        Memory Context:
        {memory_context}
        {retrieved_context}
        Client: {prompt}
        Detected Emotion: {emotion}
        Counselor:
        """
        logger.info(f"Full prompt for LLM: {full_prompt}")  # Log full prompt
        
        # Generate the response using the language model chain
        response_content = llm_chain.run({
            "system_message": client_manager_system_message.content,
            "retrieved_context": retrieved_context,
            "memory_context": memory_context,
            "user_name": user_name,
            "prompt": prompt,
            "emotion": emotion
        })

        # Log user input and response
        logger.info(f"User input: {prompt} | Response: {response_content}")

        # Save the context for future interactions
        user_memories[user_id]['buffer_memory'].save_context({"input": prompt}, {"output": response_content})
        user_memories[user_id]['summary_memory'].save_context({"input": prompt}, {"output": response_content})
        return response_content
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise

# Asynchronous function for daily check-ins to ask users how they are feeling
async def daily_check_in(application):
    for user_id, user_data in user_state.items():
        if user_data.get('awaiting_name') is False: # Check if the bot is not awaiting the user's name
            check_in_message = "Hi! Just checking in to see how you're doing today. How are you feeling?"
            logger.info(f"Sending check-in message to user {user_id}")
            await application.bot.send_message(chat_id=user_id, text=check_in_message)
        else:
            logger.info(f"Skipping user {user_id} because they are still awaiting name")

# Define the start command handler to initialize the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info("Start command received")

    # Initial welcome message
    welcome_message = "Hi there! I'm MentaAI, your intelligent NLP-based mental health assistant. 😊"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

    # Capabilities message
    capabilities_message = (
        "I'm here to support you with any mental health concerns you may have. 🧠💬\n"
        "Our conversations are private and designed to make you feel safe and heard. 🔒\n"
        "Powered by large language models, I can engage in meaningful conversations, drawing on a vast amount of knowledge to provide helpful insights.\n"
        "I utilize advanced technologies, including sentiment analysis and emotion detection, to better understand what you're experiencing. Additionally, I learn from real therapist-client transcripts using information retrieval techniques, helping to guide our interaction with empathy and relevance.\n"
        "Together, we can work on your journey toward well-being. 🌱"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=capabilities_message)

    # Request the user's name
    ask_name_message = "Firstly, I'd love to get to know you better. Could you please tell me your first name only? This will help me personalize our conversation."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ask_name_message)

    # Set the state to indicate that the bot is waiting for the user's name
    user_state[user_id] = {"awaiting_name": True}

# Define the message handler for processing user input and generating responses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_input = update.message.text.strip()

    logger.info(f"Handling message for user {user_id}, input: {user_input}")

    # Check if the user is still setting their name
    if user_id in user_state and user_state[user_id].get("awaiting_name"):
        if user_input.isalpha() and user_input.istitle():
            user_state[user_id] = {"name": user_input, "awaiting_name": False}
            ask_help_message = f"Nice to meet you, {user_input}! How are you feeling today? You can ask me something like, 'I'm feeling anxious today, can you help?'"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=ask_help_message)
        else:
            reask_name_message = "Please enter just your first name, starting with a capital letter, without any spaces or special characters."
            await context.bot.send_message(chat_id=update.effective_chat.id, text=reask_name_message)
    else:
        # Handle the actual user input
        if detect_crisis(user_input):
            await crisis_response(update, context)
        else:
            try:
                response = generate_response(user_input, user_id)
                logger.info(f"Generated response for user {user_id}: {response[:30]}...")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
            except Exception as e:
                logger.error(f"Error generating response for user {user_id}: {e}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again later.")