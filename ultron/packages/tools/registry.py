import importlib
import inspect
import pkgutil
from typing import Dict, List, Any

from .base_tool import BaseTool

class ToolRegistry:
    """Singleton registry for all Ultron tools."""
    _instance = None
    _tools: Dict[str, BaseTool]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._tools = {}
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """Registers a tool instance. Validates no name collision."""
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """Gets a tool by name. Raises KeyError with descriptive message if not found."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry. Available tools: {list(self._tools.keys())}")
        return self._tools[name]

    def list_all(self) -> List[Dict[str, Any]]:
        """Returns metadata for all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "permission_level": tool.permission_level
            }
            for tool in self._tools.values()
        ]

    def auto_discover(self) -> None:
        """Imports submodules under packages/tools/ and registers BaseTool subclasses."""
        from packages.tools import documents, code, web, che

        packages_to_scan = [
            documents,
            code,
            web,
            che
        ]

        for pkg in packages_to_scan:
            for _, module_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
                if not is_pkg:
                    full_module_name = f"{pkg.__name__}.{module_name}"
                    try:
                        module = importlib.import_module(full_module_name)
                    except ImportError as e:
                        import logging
                        logging.getLogger("ultron.tools").warning(
                            f"Skipping tool {full_module_name}: {e}"  # FIXED: isolate bad tools
                        )
                        continue
                    # Find all classes in the module that inherit from BaseTool (but aren't BaseTool itself)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseTool) and obj is not BaseTool:
                            try:
                                # Try to instantiate the tool if it doesn't take required constructor arguments
                                instance = obj()
                                self.register(instance)
                            except ValueError:
                                pass # Already registered
                            except Exception:
                                pass # Missing arguments or other instantiation error

                    # Look for instantiated instances of BaseTool in the module
                    for name, obj in inspect.getmembers(module):
                        if isinstance(obj, BaseTool):
                            try:
                                self.register(obj)
                            except ValueError:
                                pass # Already registered
                                
