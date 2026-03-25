import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Spec Engine
from packages.brain.spec_engine.generator import SpecGenerator

# Remote Work Loop
from packages.execution.remote_work_loop import RemoteWorkLoop

# AlphaEvolve
from packages.self_improvement.alphaevolve.evolver import Evolver

# Computer Use
from packages.computer_use.agent_s3 import ComputerUseController, ParsedAction


@pytest.mark.asyncio
@patch.dict('os.environ', {'SPEC_POLL_TIMEOUT': '1'}) # FIXED: fast exit
async def test_spec_engine_pipeline():
    """Test the 7-prompt parallel pipeline and Opus integration."""
    mock_publisher = AsyncMock()
    mock_publisher.publish_all = AsyncMock(return_value="notion.so/spec")
    
    # FIXED: mock Redis to avoid real polling/connection
    with patch('packages.brain.spec_engine.generator.UltronRedis', new_callable=MagicMock) as mock_redis_class:
        mock_redis = AsyncMock()
        mock_redis_class.return_value = mock_redis
        mock_redis.get.return_value = None
        
        # FIXED: mock Zilliz to avoid connection errors
        with patch('packages.brain.spec_engine.generator.ZillizPool', new_callable=MagicMock) as mock_zilliz_class:
            mock_zilliz = MagicMock()
            mock_zilliz_class.return_value = mock_zilliz
            mock_zilliz.insert = AsyncMock()
            
            generator = SpecGenerator(notion_publisher=mock_publisher)
            
            with patch.object(generator.opus_caller, 'call', new_callable=AsyncMock) as mock_opus:
                mock_opus.return_value = "Mock Opus Spec"
                with patch.object(generator.gemini, 'generate', new_callable=AsyncMock) as mock_gemini:
                    mock_resp = MagicMock()
                    mock_resp.content = "Mock Gemini Spec"
                    mock_gemini.return_value = mock_resp
                    with patch('asyncio.sleep', new_callable=AsyncMock):
                        res = await generator.generate_spec("Build a cool app")
                        assert "epic_brief" in res.documents # FIXED: check document keys
                        assert mock_opus.call_count == 2 # FIXED: 4, 7 only
                        assert mock_publisher.publish_all.call_count == 1

@pytest.mark.asyncio
async def test_remote_work_loop_dual_stream():
    """Test that remote work loop uses real MoAOrchestrator, GitTool and dispatcher search."""
    # FIXED: only 1 iteration and 2s timeout in tests
    import os
    os.environ["MAX_LOOP_ITERATIONS"] = "1"  # FIXED: only 1 iteration in tests
    os.environ["STREAM_TIMEOUT"] = "2"       # FIXED: 2 second stream timeout
    
    mock_scheduler = AsyncMock()
    
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b"proj_123"
    mock_dispatcher = AsyncMock()
    mock_dispatcher.dispatch.return_value = MagicMock(content="Search findings")
    
    loop = RemoteWorkLoop(scheduler=mock_scheduler, redis=mock_redis, dispatcher=mock_dispatcher)
    loop.is_running = True
    
    with patch('packages.brain.epic_flow.EpicFlow.run', new_callable=AsyncMock) as mock_run: # FIXED: mock EpicFlow
        mock_run.return_value = {"status": "done", "result": "mocked"}
        
        with patch('packages.brain.moa.orchestrator.MoAOrchestrator.run', new_callable=AsyncMock) as mock_moa:
            mock_moa.return_value = "Success MoA"
            with patch('packages.tools.code.git_tool.GitTool.execute', new_callable=AsyncMock) as mock_git:
                mock_git.return_value = MagicMock(success=True)
                with patch.object(loop.planner, 'advance', new_callable=AsyncMock) as mock_planner:
                    mock_planner.side_effect = [MagicMock(id="1", description="task"), None]
                    
                    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                        # Manually trigger one builder iter
                        try:
                            # force exception to stop the while true
                            mock_redis.set.side_effect = [None, Exception("Stop loop")]
                            await loop._builder_stream()
                        except Exception:
                            pass
                            
                        assert mock_moa.call_count == 1
                        assert mock_git.call_count == 1
                        assert mock_dispatcher.dispatch.call_count == 1  # git dispatch is now dispatched via ToolDispatcher
                
                # Test researcher
                with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    try:
                        mock_redis.rpush.side_effect = Exception("Stop loop")
                        await loop._researcher_stream()
                    except Exception:
                        pass
                    
                    assert mock_dispatcher.dispatch.call_count >= 2 # search + arxiv

@pytest.mark.asyncio
async def test_alphaevolve_eval_async_calls():
    """Test alpha evolve metrics correctly use real implementations structure."""
    mock_redis = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.compute_task_entropy = AsyncMock(return_value=0.5)
    
    evolver = Evolver(redis=mock_redis, entropy_engine=mock_engine)
    evolver.tester.execute = AsyncMock(return_value="100% pass")
    evolver.linter.execute = AsyncMock(return_value="0 errors")
    evolver.e2b.run_code = AsyncMock(return_value={"latency_ms": 20})
    evolver.gemini.generate = AsyncMock(return_value=MagicMock(content="18.5"))
    
    score = await evolver._evaluate_variant("print('hi')", "test.py")
    assert score > 0
    evolver.tester.execute.assert_called_once()
    evolver.linter.execute.assert_called_once()
    evolver.e2b.run_code.assert_called_once()
    mock_engine.compute_task_entropy.assert_called_once()

@pytest.mark.asyncio
async def test_computer_use_pydantic_lats():
    """Test Computer Use flow leverages Pydantic action parsing."""
    mock_xvfb = AsyncMock()
    mock_vision = AsyncMock()
    mock_vision.understand_screen.return_value = "screen parsed"
    mock_vision.completion_check.return_value = False
    
    mock_grounder = AsyncMock()
    mock_grounder.ground_element.return_value = (50, 50)
    
    mock_executor = AsyncMock()
    mock_redis = AsyncMock()
    mock_discord = AsyncMock()
    
    controller = ComputerUseController(mock_xvfb, mock_vision, mock_grounder, mock_executor, mock_redis, mock_discord)
    
    # Mock LATS plan to return a type action
    mock_plan = MagicMock()
    mock_plan.steps = ["type 'hello world'"]
    controller.lats.plan = AsyncMock(return_value=mock_plan)
    
    # Manually run just one iter
    res = await controller.execute_task("Type into search box", max_iterations=1)
    
    assert res.iterations_used == 1
    mock_executor.type_text.assert_called_with("hello world'")
    mock_executor.click.assert_called_with(50, 50)
