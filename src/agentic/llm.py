from langchain_openai import ChatOpenAI

from .settings import agents_settings


# For now, we are using OpenAI's ChatGPT model, but in the future, we need to make model selection more configurable.
llm: ChatOpenAI = ChatOpenAI(
    api_key=agents_settings.openai_api_key,
    model=agents_settings.openai_model
)
