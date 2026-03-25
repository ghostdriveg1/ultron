from abc import ABC, abstractmethod
from typing import Literal, Type
from pydantic import BaseModel, Field

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    # Class-level schema definitions to be overridden by subclasses
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    name: str
    description: str
    permission_level: Literal["ALWAYS_ALLOWED", "ENTROPY_CHECKED", "GHOST_CONFIRM", "NEVER"]
    requires_ghost_confirm: bool = False

    def __init__(self, name: str, description: str, permission_level: Literal["ALWAYS_ALLOWED", "ENTROPY_CHECKED", "GHOST_CONFIRM", "NEVER"], requires_ghost_confirm: bool = False):
        self.name = name
        self.description = description
        self.permission_level = permission_level
        self.requires_ghost_confirm = requires_ghost_confirm

    @abstractmethod
    async def execute(self, params: BaseModel) -> BaseModel:
        """Executes the tool with the given parameters and returns the result."""
        pass

    async def dry_run(self, params: BaseModel) -> str:
        """Returns a human-readable preview string without executing."""
        return f"Dry run of tool '{self.name}' with params: {params.model_dump_json()}"
