from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentsSettings(BaseSettings):
    """
    Class for storing agents settings. Read more about pydantic_settings here: https://docs.pydantic.dev/latest/concepts/pydantic_settings/.

    Attributes:
        openai_api_key (str): OpenAI API key.
        openai_model (str): OpenAI model.
    """
    model_config = SettingsConfigDict(env_prefix='AGENTS_', env_file="env/.env", extra='ignore')
    
    openai_api_key: str
    openai_model: str


agents_settings = AgentsSettings()
