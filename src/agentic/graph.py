from langgraph.graph import MessagesState, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from .agents import manager_agent
from .memory import memory


# Создаем граф состояний
graph_builder = StateGraph(MessagesState)

# Добавляем узлы
graph_builder.add_node("manager", manager_agent)
# Направляем на обработку manager_agent, если мы в начале
graph_builder.add_edge(START, "manager")

# Компилируем граф
graph: CompiledStateGraph = graph_builder.compile(checkpointer=memory)
