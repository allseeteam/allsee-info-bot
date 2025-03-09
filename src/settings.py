from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotSettings(BaseSettings):
    """
    Class for storing telegram bot settings.

    Attributes:
        token (str): Telegram bot token.
        logging_level (str): Logging level.
    """
    model_config = SettingsConfigDict(env_prefix='TELEGRAM_BOT_', env_file="env/.env", extra='ignore')
    
    token: str
    logging_level: str = "INFO"


telegram_bot_settings = TelegramBotSettings()
