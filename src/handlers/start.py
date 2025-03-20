import logging

from telegram import Update
from telegram.ext import ContextTypes


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logging.info(f"User {update.effective_user.first_name} started the conversation.")
    await update.message.reply_text(f'Привет! Я AI-ассистент в команде <a href="https://allsee.team/?utm_source=bot">AllSee.team</a> и помогу разобраться в возможностях искусственного интеллекта и кейсах моей команды. Задайте ваш первый вопрос!', parse_mode="HTML")
