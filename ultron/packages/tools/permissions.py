import json
import os
from typing import Literal

class PermissionChecker:
    """Checks permissions for tool execution."""

    def __init__(self, config_path: str = "config/permissions.json"):
        self.config_path = config_path
        self._rules = {}
        self._load_config()

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._rules = json.load(f)
        except Exception as e:
            # We fail safely; actual logic uses the level from the tool instead of config override
            pass

    def check(self, tool_name: str, permission_level: str, entropy_score: float) -> Literal["ALLOW", "DENY", "CONFIRM"]:
        """
        Determines if a tool action is permitted.
        - ALWAYS_ALLOWED: ALLOW
        - ENTROPY_CHECKED: ALLOW if entropy_score < 70 else DENY
        - GHOST_CONFIRM: CONFIRM
        - NEVER: DENY
        """
        if permission_level == "ALWAYS_ALLOWED":
            return "ALLOW"
        elif permission_level == "ENTROPY_CHECKED":
            return "ALLOW" if entropy_score < 70 else "DENY"
        elif permission_level == "GHOST_CONFIRM":
            return "CONFIRM"
        elif permission_level == "NEVER":
            return "DENY"
        return "DENY" # Default fallback
