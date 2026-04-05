"""
Ultron v3 — Brain Agent FastAPI Entry Point
Exposes /health and /run endpoints, wire TaskDispatcher on startup.
Run with:
    uvicorn packages.brain.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from packages.brain.key_rotation.pool import KeyPool
from packages.brain.task_dispatcher import TaskDispatcher

logger = logging.getLogger("ultron.main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ---------------------------------------------------------------------------
# Global singletons (initialised on startup)
# ---------------------------------------------------------------------------
_dispatcher: TaskDispatcher | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise heavy singletons once at startup."""
    global _dispatcher

    logger.info("🧠 Ultron Brain Agent — starting up...")

    # Build KeyPool from env (Gemini + Groq + OpenRouter + Cerebras + Together)
    gemini_keys  = [v for k, v in os.environ.items() if k.startswith("GEMINI_KEY_")  and v]
    groq_keys    = [v for k, v in os.environ.items() if k.startswith("GROQ_KEY_")    and v]
    openrouter   = [v for k, v in os.environ.items() if k.startswith("OPENROUTER_KEY_") and v]
    cerebras     = [v for k, v in os.environ.items() if k.startswith("CEREBRAS_KEY_") and v]
    together     = [v for k, v in os.environ.items() if k.startswith("TOGETHER_KEY_") and v]

    key_pool = KeyPool(
        gemini_keys=gemini_keys,
        groq_keys=groq_keys,
        openrouter_keys=openrouter,
        cerebras_keys=cerebras,
        together_keys=together,
    )

    # Optional: Redis client
    redis_client = None
    redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
    redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if redis_url and redis_token:
        try:
            from packages.infrastructure.redis_client import UltronRedis
            redis_client = UltronRedis(url=redis_url, token=redis_token)
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis init failed (non-fatal): {e}")

    # Optional: Zilliz vector pool
    zilliz_client = None
    try:
        from packages.infrastructure.zilliz_client import ZillizPool
        zilliz_client = ZillizPool()
        logger.info("✅ Zilliz pool ready")
    except Exception as e:
        logger.warning(f"⚠️  Zilliz init failed (non-fatal): {e}")

    _dispatcher = TaskDispatcher(
        key_pool=key_pool,
        redis=redis_client,
        zilliz=zilliz_client,
    )

    logger.info("✅ Brain Agent ready — listening on /run and /health")
    yield
    logger.info("🛑 Brain Agent shutting down...")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Ultron Brain Agent",
    version="3.0.0",
    description="Core reasoning engine for Ultron v3",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe — used by start.sh health-check loop."""
    return {"status": "ok", "service": "ultron-brain-agent"}


@app.post("/run")
async def run_task(request: Request) -> JSONResponse:
    """
    Primary task endpoint.

    Expected body (all optional except 'message'):
    {
        "message": "...",
        "channel_id": "...",
        "user_id": "...",
        "context": {},
        "priority": "NORMAL"
    }
    """
    if _dispatcher is None:
        raise HTTPException(status_code=503, detail="Dispatcher not initialised")

    try:
        payload: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not payload.get("message") and not payload.get("content"):
        raise HTTPException(status_code=422, detail="'message' field is required")

    try:
        result = await _dispatcher.dispatch(payload)
        return JSONResponse(content=result)
    except Exception as e:
        logger.exception(f"Dispatch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "Ultron Brain Agent", "version": "3.0.0", "status": "running"}
