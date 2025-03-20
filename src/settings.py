from typing import Optional, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict 
# Read more about pydantic_settings here: https://docs.pydantic.dev/latest/concepts/pydantic_settings/.


class TelegramBotSettings(BaseSettings):
    """
    Class for storing telegram bot settings

    Attributes:
        TOKEN (str): The token for the telegram bot.
        LOGGING_LEVEL (str): The logging level for the telegram bot. Default is "INFO".
    """
    model_config = SettingsConfigDict(env_prefix='TELEGRAM_BOT_', env_file="./env/.env", extra='ignore')
    
    TOKEN: str
    LOGGING_LEVEL: str = "INFO"


class LLMSettings(BaseSettings):
    """
    Class for storing LLM settings for OpenAI-compatible API

    Attributes:
        BASE_API (str): The base API URL for the LLM. Default is None (OpenAI).
        API_KEY (str): The API key for the LLM.
        MODEL (str): The model name for the LLM.
    """
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file="./env/.env", extra='ignore')

    BASE_API: Optional[str] = None
    API_KEY: str
    MODEL: str = "gpt-4o-2024-08-06"


class EmbedderSettings(BaseSettings):
    """
    Class for storing embedder settings for OpenAI-compatible API

    Attributes:
        BASE_API (str): The base API URL for the embedder. Default is None (OpenAI).
        API_KEY (str): The API key for the embedder.
        MODEL (str): The model name for the embedder.
    """
    model_config = SettingsConfigDict(env_prefix="EMBEDDER_", env_file="./env/.env", extra='ignore')

    BASE_API: Optional[str] = None
    API_KEY: str
    MODEL: str = "text-embedding-ada-002"


class CheckpointerSettings(BaseSettings):
    """
    Class for storing LangGraph checkpointer settings

    Attributes:
        DB_TYPE (str): The type of database to use for checkpointing ("sqlite" or "postgres"). Default is "sqlite".
        DB_URI (str): The URI for the database. For SQLite, this is the file path. For Postgres, this is the connection string.
    """
    model_config = SettingsConfigDict(env_prefix="CHECKPOINTER_", env_file="./env/.env", extra='ignore')

    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"  # 'sqlite' or 'postgres'
    DB_URI: str = "data/graph-memory/memory.sqlite3"  # SQLite file path or Postgres connection string    
    

class Settings(BaseSettings):
    telegram_bot: TelegramBotSettings = TelegramBotSettings()
    llm: LLMSettings = LLMSettings()
    embedder: EmbedderSettings = EmbedderSettings()
    checkpointer: CheckpointerSettings = CheckpointerSettings()


settings = Settings()
