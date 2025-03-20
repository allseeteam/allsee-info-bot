import logging
import traceback
import re

from telegram import Update
from telegram.ext import ContextTypes
from langchain_core.messages import AIMessage

from agentic.graph import graph


def convert_markdown_to_html(text: str) -> str:
    """
    Convert allowed Markdown formatting to HTML and remove disallowed formatting.
    Allowed formatting: bold, italic, links
    """
    try:
        # First convert links: [text](url) -> <a href="url">text</a>
        # This needs to happen first to avoid formatting issues in URLs
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        
        # Convert bold: **text** or __text__ -> <b>text</b>
        text = re.sub(r'\*\*(.*?)\*\*|__(.*?)__', lambda m: f'<b>{m.group(1) or m.group(2)}</b>', text)
        
        # Convert italic: *text* or _text_ -> <i>text</i>
        # Modified to avoid matching underscores in URLs or email addresses
        text = re.sub(r'(?<![a-zA-Z0-9/])\*((?!\*).+?)\*(?![a-zA-Z0-9/])|(?<![a-zA-Z0-9/.:@])_((?!_).+?)_(?![a-zA-Z0-9/])', 
                     lambda m: f'<i>{m.group(1) or m.group(2)}</i>', text)
        
        # Remove other Markdown syntax (headers, code blocks, lists, etc.)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # Remove headers
        text = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', text, flags=re.DOTALL)  # Remove code formatting
        
        return text
    
    except Exception as e:
        logging.error(f"Error converting markdown to HTML: {e}")
        # Return original text without any formatting as a fallback
        return text


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user message"""
    # For now we can use global graph instance, but in the future we need to make sure that it is not being modified by any thread and that all called methods of global graph are not-blocking.
    global graph
    logging.info(f"User {update.effective_user.first_name} sent a message.")

    # Get the user message and chat id
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    try:
        # We need to provide update to the graph for actions like send image or send file.
        # I don't know if there is better and easier way to provide non-serializable objects to the graph than through config.
        # So any contributions to make this better are welcome.
        config = {"configurable": {"thread_id": chat_id, "update": update}}
        # Using async streaming method with values stream mode which makes graph to return all state values after each step.
        # We can use ainvoke, but astream gives us ability to send text response to the user as soon as we get it from the graph.
        async for event in graph.astream(
            {
                "messages": [
                    {"role": "user", "content": user_message}
                ],
            }, 
            config, 
            stream_mode="values"
        ):
            # Some logging to understand what is happening in the graph.
            logging.info(f"\n\nAssistant: {event}")
            message = event["messages"][-1]

            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

            # If the message is AIMessage, we can send it to the user.
            # I think it would be greate to create some abstraction in the future to differentiate between agent inner thoughts and response to the user.
            if isinstance(message, AIMessage):
                processed_content = convert_markdown_to_html(message.content)
                await update.message.reply_text(processed_content, parse_mode="HTML")

    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error while processing user message: {e}")
        
    finally:
        logging.info("User message processed.")
