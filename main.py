import os
import json
# import asyncio
from telegram import Update
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)
from db import store_message, get_conversation_history, initialize_database
from botlogger import get_logger

# Load configuration file
with open("config.json") as json_file:
    config = json.load(json_file)

# Define bot token and Google token from configuration.
TELE_TOKEN = config["TELEGRAM_BOT_TOKEN"]
GOOGLE_TOKEN = config["GOOGLE_TOKEN"]
os.environ["GOOGLE_API_KEY"] = GOOGLE_TOKEN
llm = ChatGoogleGenerativeAI(model="gemini-pro")

logger = get_logger()


def answer(prompt):
    return llm.invoke(prompt).content


# Send the start message to the user.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info(f"Received start command from user {update.effective_user.id}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=config["start_message"]
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_message = update.message.text

    try:

        logger.info(f"Received message from user {user_id}: {user_message}")

        # Retrieve user conversation history and append the new message.
        user_history = await get_conversation_history(user_id)

        # Create a context-aware prompt from the user's history.
        conversation_history = "\n".join(
            [f"{role}: {message}" for role, message in user_history]
        )
        full_prompt = f"{conversation_history}\nUser: {user_message}"

        response = answer(full_prompt)


        logger.info(f"Sending response to user {user_id}: {response}")

        # Store user and bot messages in the Postgres database.
        await store_message(user_id, "user", user_message)
        await store_message(user_id, "bot", response)

        # Send the response back to the user.
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    except Exception as e:
        logger.error(f"Error processing message from user {user_id}: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred. Please try again.",
        )


def build_app():
    application = ApplicationBuilder().token(TELE_TOKEN).build()

    # Create handlers for bot commands.
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # Register handlers in the application.
    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    logger.info(f"Application built")

    application.run_polling()


if __name__ == "__main__":
    initialize_database()
    build_app()
