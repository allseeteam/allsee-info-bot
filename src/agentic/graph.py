from langgraph.graph import MessagesState, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from .agents import manager_agent
from .memory import memory


# Create a state graph for the agents
graph_builder = StateGraph(MessagesState)

# Add manager_agent to the graph
graph_builder.add_node("manager", manager_agent)
# Add entry point to the graph
graph_builder.add_edge(START, "manager")

# Compile the graph with a checkpointer
graph: CompiledStateGraph = graph_builder.compile(checkpointer=memory)
