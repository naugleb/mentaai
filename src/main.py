import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from bot_interactions import start, restart, handle_message, daily_check_in
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

#Suppress tokenizers parallelism warnings to prevent unwanted console output
os.environ["TOKENIZERS_PARALLELISM"] = "false"

#Set the timezone to UK time for scheduling tasks
uk_time = timezone('Europe/London')

#Set up logging to capture information and errors for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Bot is starting...")

#Main function to start the bot and set up scheduled tasks
def main():
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_TOKEN')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('restart', restart))  # Add the restart command handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    #Initialize the scheduler
    scheduler = AsyncIOScheduler()
    #Schedule daily check-ins at 8 PM UK time every day
    scheduler.add_job(daily_check_in, CronTrigger(hour=20, timezone=uk_time), args=[application])
    scheduler.start()
    #Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()