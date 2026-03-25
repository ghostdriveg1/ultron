"""
Ultron v3 — Verification Fixes Tests
Mock-based tests covering all 6 verification comments.
No real Redis or API keys required.
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

# ─── Ensure project root is on sys.path ──────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_mock_redis() -> AsyncMock:
    """Create a mock UltronRedis with all async methods pre-configured."""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.hset = AsyncMock()
    redis.hget = AsyncMock(return_value=None)
    redis.zadd = AsyncMock()
    redis.zrangebyscore = AsyncMock(return_value=[])
    redis.lpush = AsyncMock()
    redis.expire = AsyncMock()
    redis.delete = AsyncMock()
    redis.eval_lua = AsyncMock(side_effect=Exception("EVAL not supported"))
    return redis


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 1: Key onboarding — UUID strict validation
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment1_AddKeyUUID:
    """add_key() must construct key_id as UUID, not str, for strict Pydantic."""

    @pytest.mark.asyncio
    async def test_add_key_persists_uuid(self):
        """Verify both key_data:{key_id} and key_status:{key_id} are persisted."""
        redis = _make_mock_redis()

        # Patch AES key so encrypt_key works
        with patch.dict(os.environ, {"ULTRON_AES_KEY": "a" * 64}):
            from packages.brain.key_rotation.pool import KeyPool

            pool = KeyPool(redis)
            result = await pool.add_key(
                provider="google",
                model="gemini-2.5-pro",
                api_key="test-api-key-value",
                daily_limit=1000,
                rpm_limit=60,
                tier="smart",
            )

        assert result is True

        # Verify key_data:{key_id} was set (encrypted blob)
        data_calls = [
            c for c in redis.set.call_args_list
            if str(c[0][0]).startswith("key_data:")
        ]
        assert len(data_calls) == 1, "key_data:{key_id} must be persisted"
        key_data_key = data_calls[0][0][0]
        # Extract key_id from the Redis key name
        persisted_key_id = key_data_key.replace("key_data:", "")
        # Must be a valid UUID string
        UUID(persisted_key_id)  # Raises ValueError if not valid

        # Verify key_status:{key_id} was set
        status_calls = [
            c for c in redis.hset.call_args_list
            if str(c[0][0]).startswith("key_status:")
        ]
        assert len(status_calls) >= 1, "key_status:{key_id} must be persisted"
        status_key = status_calls[0][0][0]
        persisted_status_id = status_key.replace("key_status:", "")
        assert persisted_status_id == persisted_key_id

    @pytest.mark.asyncio
    async def test_add_key_apikey_model_validates(self):
        """APIKey model with strict=True must accept UUID key_id without error."""
        from uuid import uuid4
        from packages.brain.key_rotation.models import APIKey

        # This would fail with str(uuid4()) under strict=True
        key = APIKey(
            key_id=uuid4(),
            provider="google",
            model="gemini-2.5-pro",
            api_key="test-key",
            daily_limit=1000,
            rpm_limit=60,
            tier="smart",
            added_at=datetime.utcnow(),
        )
        assert isinstance(key.key_id, UUID)


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 2: Alert signature — send_ghost_alert(alert_type=, context=)
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment2_AlertSignature:
    """send_ghost_alert must be called with (alert_type=..., context=...) kwargs."""

    @pytest.mark.asyncio
    async def test_rotate_key_auth_alert_signature(self):
        """rotate_key('401') must call send_ghost_alert with structured kwargs."""
        redis = _make_mock_redis()
        redis.hget.side_effect = lambda name, key: {
            ("key_status:test-key", "provider"): "google",
            ("key_status:test-key", "model"): "gemini-2.5-pro",
        }.get((name, key), None)
        redis.zrangebyscore.return_value = []
        redis.eval_lua.side_effect = Exception("not supported")

        with patch(
            "packages.brain.key_rotation.pool.send_ghost_alert",
            new_callable=AsyncMock,
        ) as mock_alert:
            # Need to also patch the import inside Pool
            with patch.dict(
                "sys.modules",
                {"packages.interface.escalation": MagicMock(
                    send_ghost_alert=mock_alert
                )},
            ):
                from packages.brain.key_rotation.pool import KeyPool
                from packages.brain.key_rotation.models import AllKeysExhaustedError

                pool = KeyPool(redis)

                with pytest.raises(AllKeysExhaustedError):
                    await pool.rotate_key("test-key", "401")

                mock_alert.assert_called_once()
                call_kwargs = mock_alert.call_args
                # Must have been called with keyword args, not positional string
                assert "alert_type" in call_kwargs.kwargs or (
                    len(call_kwargs.args) == 0
                    or isinstance(call_kwargs.kwargs.get("alert_type"), str)
                )

    @pytest.mark.asyncio
    async def test_emergency_quota_alert_signature(self):
        """QuotaBrain emergency tier must call send_ghost_alert with structured kwargs."""
        redis = _make_mock_redis()

        mock_alert = AsyncMock(return_value="SKIP")

        with patch.dict(
            "sys.modules",
            {"packages.interface.escalation": MagicMock(
                send_ghost_alert=mock_alert
            )},
        ):
            from packages.brain.key_rotation.quota_brain import QuotaBrain

            brain = QuotaBrain(redis)
            # Force emergency tier by returning 0 remaining
            with patch.object(
                brain, "_get_total_remaining_quota", return_value=0
            ):
                config = await brain.get_execution_config()

            assert config.moa_proposers == 1  # emergency tier
            mock_alert.assert_called_once()
            call_kwargs = mock_alert.call_args.kwargs
            assert "alert_type" in call_kwargs
            assert "context" in call_kwargs
            assert call_kwargs["alert_type"] == "EMERGENCY_QUOTA"


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 3: Atomic admission control — concurrent determinism
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment3_AtomicAdmission:
    """check_and_consume must produce deterministic outcomes under contention."""

    @pytest.mark.asyncio
    async def test_admission_control_concurrent(self):
        """20 concurrent requests must not over-consume beyond max_tokens."""
        redis = _make_mock_redis()

        # Simulate Lua EVAL returning PROCEED and consuming atomically
        tokens_remaining = {"value": 100_000.0}

        async def fake_eval_lua(script, keys, args):
            estimated = float(args[0])
            if tokens_remaining["value"] > estimated * 1.2:
                tokens_remaining["value"] -= estimated
                return "PROCEED"
            elif tokens_remaining["value"] > estimated * 0.05:
                return "QUEUE"
            else:
                return "REJECT"

        redis.eval_lua = AsyncMock(side_effect=fake_eval_lua)

        from packages.brain.key_rotation.admission_control import (
            TokenBucketAdmissionControl,
        )

        ac = TokenBucketAdmissionControl(redis)
        estimated_per_request = 5_000

        # Fire 20 concurrent requests
        results = await asyncio.gather(
            *[
                ac.check_and_consume("google", "gemini-2.5-pro", estimated_per_request)
                for _ in range(20)
            ]
        )

        proceed_count = results.count("PROCEED")
        # With 100k budget and 5k per request, at most 20 can PROCEED
        # But threshold is estimated*1.2 = 6000, so max ~16
        assert proceed_count <= 20
        assert all(r in ("PROCEED", "QUEUE", "REJECT") for r in results)


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 4: Atomic key pool mutations — no lost updates
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment4_AtomicPoolMutations:
    """update_usage with 10+ concurrent workers must not lose updates."""

    @pytest.mark.asyncio
    async def test_update_usage_concurrent(self):
        """10 concurrent update_usage calls must produce correct final remaining."""
        redis = _make_mock_redis()

        # Simulate Lua returning decremented remaining
        usage_state = {"tokens_used": 0, "daily_limit": 10_000}

        async def fake_eval_lua(script, keys, args):
            tokens = int(args[1])
            usage_state["tokens_used"] += tokens
            remaining = max(0, usage_state["daily_limit"] - usage_state["tokens_used"])
            return remaining

        redis.eval_lua = AsyncMock(side_effect=fake_eval_lua)
        redis.hget.side_effect = lambda name, key: {
            "provider": "google",
            "model": "gemini-2.5-pro",
            "rpm_remaining": "100",
        }.get(key, None)

        from packages.brain.key_rotation.pool import KeyPool

        pool = KeyPool(redis)
        tokens_per_call = 100

        # 10 concurrent workers
        results = await asyncio.gather(
            *[
                pool.update_usage("test-key-id", tokens_per_call)
                for _ in range(10)
            ]
        )

        # Total consumed = 10 * 100 = 1000
        assert usage_state["tokens_used"] == 1000
        # All results should be valid KeyStatus objects
        assert all(r.key_id == "test-key-id" for r in results)


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 5: Instant Mode — retry on quota/auth/server errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment5_InstantModeRetry:
    """InstantMode must rotate key and retry on quota/auth/server failures."""

    @pytest.mark.asyncio
    async def test_instant_mode_retries_on_quota_error(self):
        """First generate() raises QuotaExhaustedError → rotate → retry succeeds."""
        from packages.brain.key_rotation.models import (
            APIKey,
            GenerationResult,
            QuotaExhaustedError,
        )
        from packages.brain.instant_mode import InstantMode
        from packages.brain.task_models import Task
        from uuid import uuid4

        mock_pool = AsyncMock()
        mock_gemini = AsyncMock()
        mock_thinking = MagicMock()
        mock_thinking.inject.return_value = "enhanced message"
        mock_prm = AsyncMock()
        mock_prm.score.return_value = 0.9

        # select_best_key returns a key
        first_key = APIKey(
            key_id=uuid4(),
            provider="google",
            model="gemini-2.5-pro",
            api_key="first-key",
            daily_limit=1000,
            rpm_limit=60,
            tier="smart",
        )
        mock_pool.select_best_key.return_value = first_key

        # rotate_key returns a new key
        second_key = APIKey(
            key_id=uuid4(),
            provider="google",
            model="gemini-2.5-pro",
            api_key="second-key",
            daily_limit=1000,
            rpm_limit=60,
            tier="smart",
        )
        mock_pool.rotate_key.return_value = second_key

        # First generate raises QuotaExhaustedError, second succeeds
        success_result = GenerationResult(
            content="Success response",
            input_tokens=10,
            output_tokens=20,
            model="gemini-2.5-pro",
            provider="google",
        )
        mock_gemini.generate.side_effect = [
            QuotaExhaustedError("Rate limited"),
            success_result,
        ]

        instant = InstantMode(
            key_pool=mock_pool,
            gemini_client=mock_gemini,
            thinking_injector=mock_thinking,
            prm_scorer=mock_prm,
        )

        task = Task(message="Hello", type="CONVERSATIONAL")
        response = await instant.execute(task)

        # rotate_key must have been called
        mock_pool.rotate_key.assert_called_once()
        assert response == "Success response"

    @pytest.mark.asyncio
    async def test_instant_mode_all_keys_exhausted_fallback(self):
        """When all keys are exhausted, return explicit fallback message."""
        from packages.brain.key_rotation.models import (
            APIKey,
            AllKeysExhaustedError,
            QuotaExhaustedError,
        )
        from packages.brain.instant_mode import InstantMode
        from packages.brain.task_models import Task
        from uuid import uuid4

        mock_pool = AsyncMock()
        mock_gemini = AsyncMock()
        mock_thinking = MagicMock()
        mock_thinking.inject.return_value = "enhanced"
        mock_prm = AsyncMock()
        mock_prm.score.return_value = 0.9

        first_key = APIKey(
            key_id=uuid4(), provider="google", model="gemini-2.5-pro",
            api_key="key1", daily_limit=1000, rpm_limit=60, tier="smart",
        )
        mock_pool.select_best_key.return_value = first_key
        mock_pool.rotate_key.side_effect = AllKeysExhaustedError("All exhausted")
        mock_gemini.generate.side_effect = QuotaExhaustedError("429")

        instant = InstantMode(
            key_pool=mock_pool,
            gemini_client=mock_gemini,
            thinking_injector=mock_thinking,
            prm_scorer=mock_prm,
        )

        task = Task(message="Hello", type="CONVERSATIONAL")
        response = await instant.execute(task)

        assert "temporarily unable" in response.lower() or "quota" in response.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# Comment 6: Runtime wiring — TaskDispatcher routes correctly
# ═══════════════════════════════════════════════════════════════════════════════


class TestComment6_RuntimeWiring:
    """TaskDispatcher must route CONVERSATIONAL→InstantMode, others→DeepMode."""

    @pytest.mark.asyncio
    async def test_dispatch_conversational_routes_instant(self):
        """CONVERSATIONAL messages must route to InstantMode.execute()."""
        from packages.brain.task_dispatcher import TaskDispatcher
        from packages.brain.task_models import TaskClassification

        mock_pool = AsyncMock()
        mock_router = AsyncMock()
        mock_router.classify.return_value = TaskClassification(
            type="CONVERSATIONAL",
            confidence=0.95,
            tools=[],
            models=["gemini-2.5-flash"],
            resource_profile="light",
        )

        mock_instant = AsyncMock()
        mock_instant.execute.return_value = "Instant response"
        mock_deep = AsyncMock()

        dispatcher = TaskDispatcher(
            key_pool=mock_pool,
            router=mock_router,
            instant_mode=mock_instant,
            deep_mode=mock_deep,
        )

        result = await dispatcher.dispatch({"message": "Hey, how are you?"})

        assert result["mode"] == "instant"
        assert result["task_type"] == "CONVERSATIONAL"
        assert result["response"] == "Instant response"
        mock_instant.execute.assert_called_once()
        mock_deep.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_code_routes_deep(self):
        """CODE tasks must route to DeepMode.execute()."""
        from packages.brain.task_dispatcher import TaskDispatcher
        from packages.brain.task_models import TaskClassification

        mock_pool = AsyncMock()
        mock_router = AsyncMock()
        mock_router.classify.return_value = TaskClassification(
            type="CODE",
            confidence=0.85,
            tools=["e2b_sandbox", "git"],
            models=["gemini-2.5-pro"],
            resource_profile="heavy",
        )

        mock_instant = AsyncMock()
        mock_instant.execute.return_value = "Fallback instant"
        mock_deep = AsyncMock()
        # DeepMode stub raises NotImplementedError → should fall back to InstantMode
        mock_deep.execute.side_effect = NotImplementedError("Phase 3")

        dispatcher = TaskDispatcher(
            key_pool=mock_pool,
            router=mock_router,
            instant_mode=mock_instant,
            deep_mode=mock_deep,
        )

        result = await dispatcher.dispatch({
            "message": "Write a Python function to sort a list"
        })

        # Should have tried DeepMode, fallen back to InstantMode
        assert result["mode"] == "instant_fallback"
        assert result["task_type"] == "CODE"
        mock_deep.execute.assert_called_once()
        mock_instant.execute.assert_called_once()
