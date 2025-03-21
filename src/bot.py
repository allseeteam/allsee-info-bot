import logging
import asyncio
import signal
from typing import Optional

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Application
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver, AsyncConnectionPool
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from src.settings import settings
from src.agentic.agents import manager_agent
from src.handlers import (
    handle_start,
    handle_user_message,
)


async def setup_and_start_bot() -> None:
    """Setup and start the bot."""
    # Set logging level
    logging.basicConfig(level=settings.telegram_bot.LOGGING_LEVEL)

    # Create application
    logging.info("Creating application")
    app = ApplicationBuilder().token(settings.telegram_bot.TOKEN).build()

    # Create state graph
    logging.info("Creating state graph")
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("manager", manager_agent)
    graph_builder.add_edge(START, "manager")
    
    # Set up the checkpointer, compile the graph, and add it to the application
    connection_kwargs = {"autocommit": True}
    async with AsyncConnectionPool(conninfo=settings.checkpointer.POSGRES_CONNECTION_STRING, kwargs=connection_kwargs) as pool:
        postgres_saver = AsyncPostgresSaver(pool)
        await postgres_saver.setup()
        compiled_graph = graph_builder.compile(checkpointer=postgres_saver)
        app.graph = compiled_graph

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