# T7 — MRKL Router + Complexity Detector

## Context
The MRKL Router is Ultron's brain dispatcher. Every incoming task must be classified and routed to the right pipeline. Wrong routing = wrong model for wrong task = wasted quota and bad output.

**Dependencies:** T1, T6  
**Blocks:** T9, T10 (need routing to activate)

## Files to Create
| File | Purpose |
|---|---|
| `packages/brain/mrkl_router.py` | Task classification + routing |
| `packages/brain/complexity_detector.py` | CONVERSATIONAL vs COMPLEX |
| `packages/brain/task_profiler.py` | Resource requirements per task type |

## Implementation Plan

### MRKL Router
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TaskType(Enum):
    CONVERSATIONAL = "conversational"
    CODE = "code"
    DOCUMENT = "document"
    RESEARCH = "research"
    CHE = "che"
    REMOTE_WORK = "remote_work"
    COMPLEX = "complex"
    COMPUTER_USE = "computer_use"

@dataclass
class RoutingDecision:
    task_type: TaskType
    primary_model: str
    tools_needed: list[str]
    use_moa: bool
    use_research: bool
    estimated_tokens: int
    resource_profile: str  # "light" | "medium" | "heavy"

class MRKLRouter:
    """
    Modular Reasoning, Knowledge and Language Router.
    Classifies tasks and routes to optimal pipeline.
    
    Classification is done by rule-based analysis first,
    then LLM classification for ambiguous cases.
    """
    
    def __init__(self, gemini_client, skills_library):
        self.gemini = gemini_client
        self.skills = skills_library
        
        # Keyword patterns for fast rule-based routing
        self.patterns = {
            TaskType.CHE: [
                "mass balance", "thermodynamic", "distillation",
                "hysys", "aspen", "reactor", "heat exchanger",
                "mccabe thiele", "vle", "flash", "absorption",
                "chemical engineering", "mol fraction", "enthalpy"
            ],
            TaskType.CODE: [
                "write code", "debug", "fix bug", "implement",
                "function", "class", "script", "program",
                "python", "javascript", "react", "api",
                "deploy", "github", "repository"
            ],
            TaskType.DOCUMENT: [
                "create pdf", "write report", "make presentation",
                "powerpoint", "word document", "excel sheet",
                "lab report", "latex", "summarize"
            ],
            TaskType.COMPUTER_USE: [
                "open hysys", "click", "type in", "use software",
                "gui", "desktop application", "browser"
            ],
            TaskType.REMOTE_WORK: [
                "build forever", "improve forever", "keep working",
                "autonomous", "while i sleep", "100 days",
                "eternity", "continuously"
            ]
        }
    
    async def route(self, message: str, context: dict) -> RoutingDecision:
        """
        Main routing function.
        Step 1: Rule-based classification (fast, O(n) keywords)
        Step 2: LLM classification if ambiguous (Gemini Flash)
        Step 3: Build routing decision with tools and models
        """
        task_type = self._rule_based_classify(message)
        
        if task_type is None:
            task_type = await self._llm_classify(message)
        
        return self._build_decision(task_type, message)
    
    def _rule_based_classify(self, message: str) -> Optional[TaskType]:
        message_lower = message.lower()
        
        # Check for exact keyword matches
        for task_type, keywords in self.patterns.items():
            if any(kw in message_lower for kw in keywords):
                return task_type
        
        # Short questions → conversational
        word_count = len(message.split())
        if word_count < 15 and '?' in message:
            return TaskType.CONVERSATIONAL
        
        return None  # Ambiguous, needs LLM classification
    
    def _build_decision(self, task_type: TaskType, message: str) -> RoutingDecision:
        """Build complete routing decision with all parameters."""
        
        decisions = {
            TaskType.CONVERSATIONAL: RoutingDecision(
                task_type=task_type,
                primary_model="gemini-2.5-pro",
                tools_needed=[],
                use_moa=False,
                use_research=False,
                estimated_tokens=2000,
                resource_profile="light"
            ),
            TaskType.CODE: RoutingDecision(
                task_type=task_type,
                primary_model="deepseek-coder-v3",
                tools_needed=["write_code", "run_python", "run_tests", "commit_github"],
                use_moa=True,
                use_research=True,
                estimated_tokens=15000,
                resource_profile="medium"
            ),
            TaskType.CHE: RoutingDecision(
                task_type=task_type,
                primary_model="gemini-2.5-pro",
                tools_needed=["mass_balance_tool", "thermo_tool", "nist_tool", "create_pdf"],
                use_moa=True,
                use_research=True,
                estimated_tokens=20000,
                resource_profile="medium"
            ),
            # ... other task types
        }
        
        return decisions.get(task_type, decisions[TaskType.CONVERSATIONAL])
```

## Acceptance Criteria
- [ ] "what is osmosis?" → CONVERSATIONAL within 50ms
- [ ] "build me a website" → CODE|COMPLEX within 100ms  
- [ ] "calculate mass balance for HCl absorption" → CHE within 50ms
- [ ] Ambiguous messages classified by LLM within 500ms
- [ ] Tool list appropriate for each task type
- [ ] Resource profile used by execution engine for routing

## Edge Cases
- Mixed task (code + document): return COMPLEX, use all tools
- Very long message: truncate to 500 chars for keyword analysis
- Non-English message: detect language, translate keywords
