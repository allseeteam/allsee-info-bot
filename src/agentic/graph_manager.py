from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver, AsyncConnectionPool
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from .agents import manager_agent


class GraphManager:
    def __init__(self):
        self.graph_builder = StateGraph(MessagesState)
        self._setup_graph()
        self.compiled_graph: Optional[CompiledStateGraph] = None
        self.postgres_saver: Optional[AsyncPostgresSaver] = None
        self._postgres_connection_pool = None
        self.postgres_conn_string: str = None
    

    def _setup_graph(self):
        """Setup the graph structure"""
        # Add manager_agent to the graph
        self.graph_builder.add_node("manager", manager_agent)
        # Add entry point to the graph
        self.graph_builder.add_edge(START, "manager")


    async def initialize(self, postgres_conn_string: str):
        """Initialize the graph manager with Checkpointer PostgreSQL connection string"""
        self.postgres_conn_string = postgres_conn_string
        return self


    async def __aenter__(self):
        """Initialize PostgreSQL connection pool and saver"""
        self._postgres_connection_pool = await AsyncConnectionPool(conninfo=self.postgres_conn_string, kwargs={"autocommit": True}).__aenter__()
        self.postgres_saver = AsyncPostgresSaver(self._postgres_connection_pool)
        await self.postgres_saver.setup()
        self.compiled_graph = self.graph_builder.compile(checkpointer=self.postgres_saver)
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup PostgreSQL connection pool"""
        self.compiled_graph = None
        
        if self.postgres_saver and self._postgres_connection_pool:
            await self._postgres_connection_pool.__aexit__(exc_type, exc_val, exc_tb)
            self._postgres_connection_pool = None
            self.postgres_saver = None


    def get_graph(self) -> CompiledStateGraph:
        """Get the compiled graph instance"""
        if not self.compiled_graph:
            raise RuntimeError("Graph not initialized. Use 'async with GraphManager().initialize()' first")
        return self.compiled_graph


# Create a singleton instance
graph_manager = GraphManager()
