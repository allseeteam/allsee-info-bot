import logging
from typing import Optional

from pydantic import BaseModel, Field
from telegram import Update

from langchain_core.tools import StructuredTool
from langchain_core.runnables.config import RunnableConfig


class DocumentReply(BaseModel):
    """Pydantic model for sending a document to a user"""
    reply_document_path: str = Field(description="Путь к документу, который будет отправлен пользователю")
    reply_text: Optional[str] = Field(description="Текст сообщения для пользователя, который будет отправлен вместе с документом", default=None)


class ReplyResult(BaseModel):
    """Result of sending a message to a user"""
    success: bool = Field(description="Флаг успешной отправки сообщения")
    error: str | None = Field(description="Текст ошибки, если отправка не удалась")


async def send_document_to_user(reply_document_path: str, reply_text: Optional[str], config: RunnableConfig) -> ReplyResult:
    """A tool for sending a document to a user"""
    # Try to get the update from InjectedState and send the document to the user
    try:
        update: Update = config["configurable"].get("update")
        print("\n\n-----")
        print(update)
        print(reply_text)
        print(reply_document_path)
        await update.message.reply_document(
            document=reply_document_path,
            caption=reply_text,
            parse_mode="HTML",
        )

    # Handling error if sending the message fails
    except Exception as e:
        logging.error(f"Failed to send message to user: {e}")
        return ReplyResult(success=False, error=str(e))
    
    # Returning success result
    finally:
        return ReplyResult(success=True, error=None)


# Creating a structured tool for sending a document to a user
send_document_to_user_tool = StructuredTool.from_function(
    coroutine=send_document_to_user,
    name="SendDocumentToUser",
    description="Отправить пользователю документ с опциональным тестовым сопровождением (использовать, если нужно отправить пользователю какой-то файл)",
    args_schema=DocumentReply,
)
