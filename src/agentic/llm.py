from langchain_openai import ChatOpenAI

from ..settings import settings


# For now, we are using OpenAI's ChatGPT model, but in the future, we need to make model selection more configurable.
llm: ChatOpenAI = ChatOpenAI(
    api_key=settings.llm.API_KEY,
    model=settings.llm.MODEL,
    base_url=settings.llm.BASE_API,
)
