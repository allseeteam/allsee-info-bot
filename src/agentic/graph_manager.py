from typing import Optional, Union, Literal

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver, AsyncConnectionPool
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.graph.state import CompiledStateGraph

from .agents import manager_agent


class GraphManager:
    def __init__(self):
        self.graph_builder = StateGraph(MessagesState)
        self._setup_graph()
        self.compiled_graph: Optional[CompiledStateGraph] = None
        self.saver: Optional[Union[AsyncSqliteSaver, AsyncPostgresSaver]] = None
        self._pool = None
        self._sqlite_ctx = None
        self.db_type: str = None
        self.db_uri: str = None
    

    def _setup_graph(self):
        """Setup the graph structure"""
        # Add manager_agent to the graph
        self.graph_builder.add_node("manager", manager_agent)
        # Add entry point to the graph
        self.graph_builder.add_edge(START, "manager")


    async def initialize(self, db_type: Literal["sqlite", "postgres"], db_uri: str):
        """Store initialization parameters for later use"""
        self.db_type = db_type
        self.db_uri = db_uri
        return self


    async def __aenter__(self):
        """Support for async context manager protocol"""
        if self.db_type.lower() == "sqlite":
            self._sqlite_ctx = AsyncSqliteSaver.from_conn_string(self.db_uri)
            self.saver = await self._sqlite_ctx.__aenter__()

        elif self.db_type.lower() == "postgres":
            self._pool = await AsyncConnectionPool(conninfo=self.db_uri, kwargs={"autocommit": True}).__aenter__()
            self.saver = AsyncPostgresSaver(self._pool)
            await self.saver.setup()

        else:
            raise ValueError(f"Unsupported database type: {self.db_type}. Use 'sqlite' or 'postgres'.")
        
        self.compiled_graph = self.graph_builder.compile(checkpointer=self.saver)
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support for async context manager protocol cleanup"""
        self.compiled_graph = None

        if self.saver:
            if isinstance(self.saver, AsyncSqliteSaver) and self._sqlite_ctx:
                # SQLite saver cleanup
                await self._sqlite_ctx.__aexit__(exc_type, exc_val, exc_tb)
                self._sqlite_ctx = None

            elif self._pool:
                # Postgres pool cleanup
                await self._pool.__aexit__(exc_type, exc_val, exc_tb)
                self._pool = None

            self.saver = None


    def get_graph(self) -> CompiledStateGraph:
        """Get the compiled graph instance"""
        if not self.compiled_graph:
            raise RuntimeError("Graph not initialized. Use 'async with GraphManager().initialize()' first")
        return self.compiled_graph


# Create a singleton instance
graph_manager = GraphManager()
