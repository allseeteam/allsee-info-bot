# AllSee info bot

This bot is used to provide information about AllSee products and services but can be adapted for your own needs (see instructions below).

## Features
1. Bot can reply to user according to the provided system prompt.
2. Bot can send hyperlinks.
3. Bot can send any files.
4. Bot can call retrieval to get information from provided documents.

## Technologies
1. Bot is using [python-telegram-bot](https://python-telegram-bot.org/) for interaction with Telegram bot API. 
2. Bot is using [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management. All settings are stored in the `.env` file.
3. Bot is using [LangGraph](https://langchain-ai.github.io/langgraph/) for managing conversations, function calling and so on.
4. Bot is using ChatOpenAI from langchain_openai as LLM-wrapper. It can be easily replaced with other LLMs by updating [llm.py](src/agentic/llm.py) file.
5. Bot is using Chroma from langchain_chroma for vector database (for retrieval purpose). Currently, all retrieval-related code is placed in [retrieval.py](src/agentic/agents/manager/tools/retrieval.py).

## How you can set this bot up
1. Clone the repository
    ```shell
    git clone https://github.com/allseeteam/allsee-info-bot
    cd allsee-info-bot
    ```
2. Create a virtual environment, activate it and install dependencies. Tested on python 3.11.11
    ```shell
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3. Create a `.env` file from [.env.example](env/.env.example) and fill in the required variables (instruction for each variable is in the file):
    ```shell
    cp ./env/.env.example ./env/.env
    nano ./env/.env
    ```
4. You need to add data to `data` folder and update paths in [retrieval.py](src/agentic/agents/manager/tools/retrieval.py) and [manager.py](src/agentic/agents/manager/manager.py) files. Files used in [retrieval.py](src/agentic/agents/manager/tools/retrieval.py) should be in `.md` format, where each part is splitted with "#" symbol. For example:
    ```markdown
    # Part 1
    This is part 1 of the document.
    
    # Part 2
    This is part 2 of the document.
    
    # Part 3
    This is part 3 of the document.
    ```
    You can use any number of parts, but it should be in `.md` format. You can also use other formats like `.txt`, but you will need to update the code in [retrieval.py](src/agentic/agents/manager/tools/retrieval.py) file.
5. Start the bot
    ```shell
    python src/bot.py
    ```
## Work to be done
1. For now, bot is using SYNC RAM-saver to store all conversations in memory. This is not optimal for production use. In the future we need to implement async saver based on SQLite or PostgreSQL. It can be done using prebuild langgraph instruments like [AsyncSqliteSaver](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver) or [AsyncPostgresSaver](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver).
2. Some parts of the code are using global variables like llm from [llm.py](src/agentic/llm.py) and other staff. In the future we need to make sure that all global variables are safe from changes from other threads and make sure that methods from globally used objects like llm and graph are not-blocking (e.g. using async methods).
3. For now setup of Chroma is hardcoded in [retrieval.py](src/agentic/agents/manager/tools/retrieval.py). In the future we need to make config for providing documents which we want to use for retrieval. For now we are using Chroma with default settings and no documents as well as other configurations.
4. We need to make our agents more configurable. Create separate config files for storing system prompts and other settings.
5. We need to add agent for processing structured data like tables.
6. We need to properly handle all runtime errors and exceptions.
7. We need to properly handle non-parseable formating from llm.

# How you can customize this bot
1. You can change LLM used in [llm.py](src/agentic/llm.py)
2. You can update manager agent system prompt in [manager.py](src/agentic/agents/manager/manager.py)
3. You can add new manager-agent tools or update existing ones in [tools](src/agentic/agents/manager/tools). 
4. You can add new agents to by creating the like modules and setting handshakes between them like in [this doc](https://langchain-ai.github.io/langgraph/how-tos/agent-handoffs/).