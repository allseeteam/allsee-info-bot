from langgraph.checkpoint.memory import MemorySaver


# We are using SYNC saver to save conversation history in RAM. In the future, we may need to make our saver async and use something like SQLite or Postgres to save conversation history in a database.
# There is some worth-to-mention details about async savers. Here are some good starting points:
# - https://github.com/langchain-ai/langgraph/discussions/1211
# - https://github.com/langchain-ai/langchain/discussions/23630
memory: MemorySaver = MemorySaver()
