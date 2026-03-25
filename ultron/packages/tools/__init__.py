from .base_tool import BaseTool
from .registry import ToolRegistry
from .dispatcher import ToolDispatcher

# Instantiate registry and discover tools on startup
registry = ToolRegistry()
registry.auto_discover()

__all__ = ["BaseTool", "ToolRegistry", "ToolDispatcher", "registry"]
