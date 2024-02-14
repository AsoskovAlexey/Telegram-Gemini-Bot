import logging
import os
import json
from telegram import Update
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

# Load configuration file to retrieve bot token.
with open("config.json") as json_file:
    config = json.load(json_file)

# Define bot token and Google token from configuration.
TELE_TOKEN = config['TELEGRAM_BOT_TOKEN']
GOOGLE_TOKEN = config['GOOGLE_TOKEN']
os.environ["GOOGLE_API_KEY"] = GOOGLE_TOKEN
llm = ChatGoogleGenerativeAI(model="gemini-pro")

# Configure logging module.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get the logger for the bot.
logger = logging.getLogger(__name__)


def answer(prompt):
    return llm.invoke(prompt).content


# Define asynchronous functions for bot commands.
async def start(update, context):
    # Log the start command.
    logger.info(f"Received start command from user {update.effective_user.id}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=config["start_message"])


async def echo(update, context):
    # Log the incoming message.
    logger.info(f"Received message from user {update.effective_user.id}: {update.message.text}")

    # Get the answer.
    response = answer(update.message.text)

    # Log the response.
    logger.info(f"Sending response to user {update.effective_user.id}: {response}")

    # Send the response.
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN).build()

    # Create handlers for bot commands.
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # Register handlers in the application.
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    # Run the application to start polling for updates.
    application.run_polling()
