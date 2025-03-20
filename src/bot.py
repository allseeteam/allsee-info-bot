import logging
import asyncio
import signal

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application

from src.settings import settings
from src.agentic.graph_manager import graph_manager
from src.handlers import (
    handle_start,
    handle_user_message,
)


async def cleanup_graph(application: Application) -> None:
    """Cleanup graph during application shutdown"""
    if hasattr(application, 'graph_manager'):
        await graph_manager.__aexit__(None, None, None)
        application.graph_manager = None


async def shutdown(app: Application, signal: str = None):
    """Cleanup and shutdown the application"""
    logging.info(f"Received signal: {signal}, shutting down...")

    try:
        # First stop the updater
        if app.updater and app.updater.running:
            await app.updater.stop()
        # Then stop the application
        if app.running:
            await app.stop()
        # Finally cleanup the graph
        await cleanup_graph(app)

    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
        raise


async def setup_and_start_bot() -> None:
    """Setup and start the bot."""
    # Set logging level
    logging.basicConfig(level=settings.telegram_bot.LOGGING_LEVEL)

    # Create application
    logging.info("Creating application")
    app = ApplicationBuilder().token(settings.telegram_bot.TOKEN).build()

    # Initialize graph before starting bot
    logging.info("Initializing graph manager")
    await graph_manager.initialize(settings.checkpointer.DB_TYPE, settings.checkpointer.DB_URI)

    # Set up graph manager context
    async with graph_manager as manager:
        app.graph_manager = manager

        # Add handlers
        logging.info("Adding handlers")
        app.add_handler(CommandHandler("start", handle_start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

        try:
            # Start the bot
            logging.info("Starting bot")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            
            # Block until a signal is received
            stop_signal = asyncio.Event()
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(signal.SIGINT, stop_signal.set)
            loop.add_signal_handler(signal.SIGTERM, stop_signal.set)
            await stop_signal.wait()
            
        finally:
            logging.info("Shutting down...")
            await shutdown(app)


def main():
    """Main function to run the bot"""
    try:
        asyncio.run(setup_and_start_bot())

    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user")

    except Exception as e:
        logging.error(f"Bot stopped due to error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
