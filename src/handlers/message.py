import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes
from langchain_core.messages import AIMessage

from agentic.graph import graph


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user message"""
    global graph
    logging.info(f"User {update.effective_user.first_name} sent a message.")
    
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    try:
        config = {"configurable": {"thread_id": chat_id, "update": update}}
        async for event in graph.astream(
            {
                "messages": [
                    {"role": "user", "content": user_message}
                ],
            }, 
            config, 
            stream_mode="values"
        ):
            logging.info(f"\n\nAssistant: {event}")
            message = event["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
            if isinstance(message, AIMessage):
                await update.message.reply_text(message.content, parse_mode="HTML")
    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error while processing user message: {e}")
    finally:
        logging.info("User message processed.")
