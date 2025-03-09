from langchain_openai import ChatOpenAI

from .settings import agents_settings


llm: ChatOpenAI = ChatOpenAI(
    api_key=agents_settings.openai_api_key,
    model=agents_settings.openai_model
)
