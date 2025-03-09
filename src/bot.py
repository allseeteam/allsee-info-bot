import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from settings import telegram_bot_settings
from handlers import (
    handle_start,
    handle_user_message,
)


def setup_and_start_bot() -> None:
    """Setup and start the bot."""
    # Set logging level
    logging.basicConfig(level=telegram_bot_settings.logging_level)

    # Create application
    logging.info("Creating application")
    app = ApplicationBuilder().token(telegram_bot_settings.token).build()
    
    # Add handlers
    logging.info("Adding handlers")
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    
    # Run the bot
    logging.info("Starting bot")
    app.run_polling()


if __name__ == "__main__":
    setup_and_start_bot()
