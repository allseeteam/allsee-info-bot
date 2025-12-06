import logging

from telegram import Update
from telegram.ext import ContextTypes


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logging.info(f"User {update.effective_user.first_name} started the conversation.")
    await update.message.reply_text(
        'Привет! <a href="https://allsee.team/?utm_source=bot">AllSee</a> запускает продукты c искусственным интеллектом для роста бизнеса. Хотите увидеть, как это происходит в реальных кейсах, или сразу перейдем к вашей задаче?',
        parse_mode="HTML"
    )
