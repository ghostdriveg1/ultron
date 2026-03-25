# T8 — Instant Mode (Conversational Response)

## Context
When Ghost asks a question and is waiting for an answer, Ultron must respond in under 12 seconds. This is Instant Mode — single model, thinking injection, no MoA overhead.

**Dependencies:** T6, T7  
**Blocks:** Nothing (standalone path)

## Files to Create
| File | Purpose |
|---|---|
| `packages/brain/instant_mode.py` | Single model fast response |
| `packages/brain/thinking_injector.py` | CoT prompt injection |
| `packages/brain/prm_scorer.py` | Step-level quality scoring |

## Implementation Plan

### Instant Mode
```python
class InstantMode:
    """
    Fast response path for conversational queries.
    Single Gemini 2.5 Pro call with thinking injection.
    
    Quality: 87% (good for conversational)
    Speed: 8-12 seconds
    Tokens: ~2000 average
    """
    
    async def respond(self, message: str, context_passport: dict) -> str:
        # 1. Load core memory (always available)
        core_context = context_passport.get("core_memory", {})
        
        # 2. Inject thinking prompt
        enhanced_prompt = self.thinking_injector.inject(message)
        
        # 3. Single model call
        key = await self.key_pool.get_key("google", "gemini-2.5-pro")
        response = await self.gemini.generate(
            prompt=enhanced_prompt,
            system=self._build_system_prompt(core_context),
            api_key=key,
            max_tokens=2000
        )
        
        # 4. PRM score the response
        score = await self.prm_scorer.score(message, response)
        
        # 5. If score < 0.7: regenerate once
        if score < 0.7:
            response = await self._regenerate(message, core_context)
        
        return response

### Thinking Injector
```python
THINKING_TEMPLATE = """
Before answering, think step by step:
1. What is the core question being asked?
2. What context from my memory is relevant?
3. What would be the naive wrong answer?
4. What edge cases or nuances exist?
5. What is the most accurate, helpful response?

Now answer:
{original_message}
"""

def inject(self, message: str) -> str:
    return THINKING_TEMPLATE.format(original_message=message)
```

## Acceptance Criteria
- [ ] Response time < 12 seconds for 95th percentile
- [ ] Ghost-specific context included in every response
- [ ] Low-quality responses (PRM < 0.7) regenerated automatically
- [ ] Tokens used < 3000 per instant mode call

